"""Anomaly detection utilities using statistical methods."""

from __future__ import annotations

from typing import Literal, Optional

import numpy as np
import pandas as pd

DetectionMethod = Literal["iqr", "zscore", "both"]


class AnomalyDetectorError(Exception):
    """Raised when anomaly detection operations fail."""


class AnomalyDetector:
    """Detect outliers in numeric columns using IQR and Z-score methods.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing numeric columns to analyze.
    iqr_multiplier : float, default 1.5
        IQR fence multiplier (1.5 = mild outliers, 3.0 = extreme).
    zscore_threshold : float, default 3.0
        Absolute Z-score above which a value is flagged as an anomaly.

    Examples
    --------
    >>> detector = AnomalyDetector(df)
    >>> flags = detector.detect(columns=["revenue"], method="iqr")
    >>> summary = detector.get_summary()
    """

    def __init__(
        self,
        df: pd.DataFrame,
        iqr_multiplier: float = 1.5,
        zscore_threshold: float = 3.0,
    ) -> None:
        if not isinstance(df, pd.DataFrame):
            raise AnomalyDetectorError(
                f"Expected pandas DataFrame, got {type(df).__name__}."
            )
        if df.empty:
            raise AnomalyDetectorError("Input DataFrame is empty.")
        if iqr_multiplier <= 0:
            raise AnomalyDetectorError("iqr_multiplier must be positive.")
        if zscore_threshold <= 0:
            raise AnomalyDetectorError("zscore_threshold must be positive.")

        self._df = df.copy()
        self.iqr_multiplier = iqr_multiplier
        self.zscore_threshold = zscore_threshold
        self._results: Optional[pd.DataFrame] = None

    @property
    def data(self) -> pd.DataFrame:
        """Return a copy of the input DataFrame."""
        return self._df.copy()

    @property
    def results(self) -> Optional[pd.DataFrame]:
        """Return the latest detection results, or None if not yet run."""
        return self._results.copy() if self._results is not None else None

    def detect(
        self,
        columns: Optional[list[str]] = None,
        method: DetectionMethod = "both",
    ) -> pd.DataFrame:
        """Detect anomalies in specified numeric columns.

        Parameters
        ----------
        columns : list of str, optional
            Columns to analyze. Defaults to all numeric columns.
        method : {"iqr", "zscore", "both"}, default "both"
            Detection method to apply.

        Returns
        -------
        pd.DataFrame
            Boolean mask aligned with input rows. Columns suffixed with
            ``_iqr_anomaly``, ``_zscore_anomaly``, or ``_anomaly`` (combined).

        Raises
        ------
        AnomalyDetectorError
            If method is invalid or no numeric columns are available.
        """
        valid_methods = {"iqr", "zscore", "both"}
        if method not in valid_methods:
            raise AnomalyDetectorError(
                f"Invalid method '{method}'. Choose from {sorted(valid_methods)}."
            )

        target_cols = self._resolve_numeric_columns(columns)
        result = pd.DataFrame(index=self._df.index)

        if method in ("iqr", "both"):
            for col in target_cols:
                result[f"{col}_iqr_anomaly"] = self._detect_iqr(self._df[col])

        if method in ("zscore", "both"):
            for col in target_cols:
                result[f"{col}_zscore_anomaly"] = self._detect_zscore(
                    self._df[col]
                )

        if method == "both":
            iqr_cols = [c for c in result.columns if c.endswith("_iqr_anomaly")]
            zscore_cols = [
                c for c in result.columns if c.endswith("_zscore_anomaly")
            ]
            for iqr_col, zscore_col in zip(iqr_cols, zscore_cols):
                base = iqr_col.replace("_iqr_anomaly", "")
                result[f"{base}_anomaly"] = (
                    result[iqr_col] | result[zscore_col]
                )

        self._results = result
        return result.copy()

    def get_anomaly_rows(
        self,
        columns: Optional[list[str]] = None,
        method: DetectionMethod = "both",
    ) -> pd.DataFrame:
        """Return rows flagged as anomalous.

        Parameters
        ----------
        columns : list of str, optional
            Columns to analyze.
        method : {"iqr", "zscore", "both"}, default "both"
            Detection method.

        Returns
        -------
        pd.DataFrame
            Subset of input data containing anomalous rows.
        """
        flags = self.detect(columns=columns, method=method)
        anomaly_cols = [
            c
            for c in flags.columns
            if c.endswith("_anomaly") or c.endswith("_iqr_anomaly") or c.endswith("_zscore_anomaly")
        ]
        if method == "both":
            anomaly_cols = [c for c in flags.columns if c.endswith("_anomaly")]

        if not anomaly_cols:
            anomaly_cols = list(flags.columns)

        row_mask = flags[anomaly_cols].any(axis=1)
        return self._df.loc[row_mask].copy()

    def get_summary(self) -> pd.DataFrame:
        """Summarize anomaly counts per column from the latest detection run.

        Returns
        -------
        pd.DataFrame
            Summary with column, method, anomaly_count, and anomaly_pct.

        Raises
        ------
        AnomalyDetectorError
            If detect() has not been called yet.
        """
        if self._results is None:
            raise AnomalyDetectorError(
                "No detection results available. Call detect() first."
            )

        total = len(self._df)
        rows: list[dict[str, object]] = []

        for col in self._results.columns:
            count = int(self._results[col].sum())
            rows.append(
                {
                    "column": col,
                    "anomaly_count": count,
                    "anomaly_pct": round((count / total) * 100, 2) if total else 0.0,
                }
            )

        return pd.DataFrame(rows).sort_values(
            "anomaly_count", ascending=False
        ).reset_index(drop=True)

    def _detect_iqr(self, series: pd.Series) -> pd.Series:
        """Flag values outside IQR fences."""
        clean = series.dropna()
        if clean.empty:
            return pd.Series(False, index=series.index)

        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            return pd.Series(False, index=series.index)

        lower = q1 - self.iqr_multiplier * iqr
        upper = q3 + self.iqr_multiplier * iqr
        return (series < lower) | (series > upper)

    def _detect_zscore(self, series: pd.Series) -> pd.Series:
        """Flag values whose absolute Z-score exceeds the threshold."""
        clean = series.dropna()
        if clean.empty or len(clean) < 2:
            return pd.Series(False, index=series.index)

        mean = clean.mean()
        std = clean.std(ddof=0)

        if std == 0 or np.isnan(std):
            return pd.Series(False, index=series.index)

        zscores = np.abs((series - mean) / std)
        return zscores > self.zscore_threshold

    def _resolve_numeric_columns(
        self, columns: Optional[list[str]]
    ) -> list[str]:
        """Return validated numeric column names."""
        if columns is None:
            numeric_cols = self._df.select_dtypes(include=np.number).columns.tolist()
            if not numeric_cols:
                raise AnomalyDetectorError(
                    "No numeric columns found in DataFrame."
                )
            return numeric_cols

        missing = set(columns) - set(self._df.columns)
        if missing:
            raise AnomalyDetectorError(
                f"Columns not found in DataFrame: {sorted(missing)}"
            )

        non_numeric = [
            c for c in columns if not pd.api.types.is_numeric_dtype(self._df[c])
        ]
        if non_numeric:
            raise AnomalyDetectorError(
                f"Non-numeric columns cannot be analyzed: {non_numeric}"
            )

        return columns
