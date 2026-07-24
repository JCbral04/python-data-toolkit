"""Data cleaning utilities for tabular datasets."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union

import numpy as np
import pandas as pd

FillStrategy = Literal["mean", "median", "mode", "zero", "drop"]
DuplicateStrategy = Literal["first", "last", "none"]


class DataCleanerError(Exception):
    """Raised when data cleaning operations fail."""


class DataCleaner:
    """Clean and prepare pandas DataFrames for analysis.

    Handles missing values, duplicate rows, and type conversions with
    configurable strategies and validation.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to clean. A copy is stored internally.

    Examples
    --------
    >>> cleaner = DataCleaner(df)
    >>> cleaned = cleaner.handle_missing_values(strategy="median")
    >>> cleaned = cleaner.remove_duplicates()
    """

    def __init__(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise DataCleanerError(
                f"Expected pandas DataFrame, got {type(df).__name__}."
            )
        if df.empty:
            raise DataCleanerError("Input DataFrame is empty.")
        self._df = df.copy()

    @property
    def data(self) -> pd.DataFrame:
        """Return a copy of the current cleaned DataFrame."""
        return self._df.copy()

    def handle_missing_values(
        self,
        strategy: FillStrategy = "mean",
        columns: Optional[list[str]] = None,
        fill_value: Optional[Any] = None,
    ) -> pd.DataFrame:
        """Handle missing values using the specified strategy.

        Parameters
        ----------
        strategy : {"mean", "median", "mode", "zero", "drop"}, default "mean"
            How to impute or remove missing values.
        columns : list of str, optional
            Subset of columns to process. Defaults to all columns.
        fill_value : Any, optional
            Custom fill value when strategy is not applicable for a column type.

        Returns
        -------
        pd.DataFrame
            DataFrame with missing values handled.

        Raises
        ------
        DataCleanerError
            If strategy is invalid or specified columns do not exist.
        """
        valid_strategies = {"mean", "median", "mode", "zero", "drop"}
        if strategy not in valid_strategies:
            raise DataCleanerError(
                f"Invalid strategy '{strategy}'. Choose from {sorted(valid_strategies)}."
            )

        target_cols = self._resolve_columns(columns)

        if strategy == "drop":
            self._df = self._df.dropna(subset=target_cols)
            return self.data

        for col in target_cols:
            if self._df[col].isna().sum() == 0:
                continue

            if strategy == "zero":
                if pd.api.types.is_numeric_dtype(self._df[col]):
                    self._df[col] = self._df[col].fillna(0)
                else:
                    self._df[col] = self._df[col].fillna("")
            elif strategy == "mean":
                if not pd.api.types.is_numeric_dtype(self._df[col]):
                    raise DataCleanerError(
                        f"Column '{col}' is not numeric; cannot apply 'mean' strategy."
                    )
                self._df[col] = self._df[col].fillna(self._df[col].mean())
            elif strategy == "median":
                if not pd.api.types.is_numeric_dtype(self._df[col]):
                    raise DataCleanerError(
                        f"Column '{col}' is not numeric; cannot apply 'median' strategy."
                    )
                self._df[col] = self._df[col].fillna(self._df[col].median())
            elif strategy == "mode":
                mode_vals = self._df[col].mode(dropna=True)
                if mode_vals.empty:
                    if fill_value is not None:
                        self._df[col] = self._df[col].fillna(fill_value)
                    else:
                        raise DataCleanerError(
                            f"Column '{col}' has no mode and no fill_value was provided."
                        )
                else:
                    self._df[col] = self._df[col].fillna(mode_vals.iloc[0])

        return self.data

    def remove_duplicates(
        self,
        subset: Optional[list[str]] = None,
        keep: DuplicateStrategy = "first",
    ) -> pd.DataFrame:
        """Remove duplicate rows from the DataFrame.

        Parameters
        ----------
        subset : list of str, optional
            Column names to consider when identifying duplicates.
        keep : {"first", "last", "none"}, default "first"
            Which duplicate to retain.

        Returns
        -------
        pd.DataFrame
            DataFrame with duplicates removed.

        Raises
        ------
        DataCleanerError
            If keep strategy is invalid or subset columns do not exist.
        """
        valid_keep = {"first", "last", "none"}
        if keep not in valid_keep:
            raise DataCleanerError(
                f"Invalid keep '{keep}'. Choose from {sorted(valid_keep)}."
            )

        if subset is not None:
            self._resolve_columns(subset)

        keep_arg: Union[bool, Literal["first", "last"]] = False if keep == "none" else keep
        self._df = self._df.drop_duplicates(subset=subset, keep=keep_arg)
        return self.data

    def convert_types(
        self,
        dtype_map: dict[str, str],
        errors: Literal["raise", "coerce"] = "coerce",
    ) -> pd.DataFrame:
        """Convert column dtypes according to a mapping.

        Parameters
        ----------
        dtype_map : dict
            Mapping of column name to target dtype string
            (e.g. ``{"age": "int64", "price": "float64", "date": "datetime64[ns]"}``).
        errors : {"raise", "coerce"}, default "coerce"
            If ``"raise"``, invalid conversions raise ``DataCleanerError``.
            If ``"coerce"``, invalid values become NaN.

        Returns
        -------
        pd.DataFrame
            DataFrame with converted column types.

        Raises
        ------
        DataCleanerError
            If columns are missing or conversion fails with errors="raise".
        """
        if not dtype_map:
            raise DataCleanerError("dtype_map must not be empty.")

        self._resolve_columns(list(dtype_map.keys()))

        for col, target_dtype in dtype_map.items():
            try:
                if target_dtype.startswith("datetime"):
                    self._df[col] = pd.to_datetime(
                        self._df[col], errors=errors
                    )
                elif target_dtype == "category":
                    self._df[col] = self._df[col].astype("category")
                elif target_dtype in ("int64", "int32", "float64", "float32", "bool", "str"):
                    if errors == "coerce" and target_dtype.startswith("int"):
                        self._df[col] = pd.to_numeric(
                            self._df[col], errors="coerce"
                        ).astype("float64")
                        if self._df[col].notna().all() and (
                            self._df[col] % 1 == 0
                        ).all():
                            self._df[col] = self._df[col].astype(target_dtype)
                    else:
                        self._df[col] = self._df[col].astype(target_dtype)
                else:
                    self._df[col] = self._df[col].astype(target_dtype)
            except (ValueError, TypeError) as exc:
                if errors == "raise":
                    raise DataCleanerError(
                        f"Failed to convert column '{col}' to '{target_dtype}': {exc}"
                    ) from exc

        return self.data

    def get_missing_summary(self) -> pd.DataFrame:
        """Return a summary of missing values per column.

        Returns
        -------
        pd.DataFrame
            Columns: ``column``, ``missing_count``, ``missing_pct``.
        """
        missing = self._df.isna().sum()
        total = len(self._df)
        summary = pd.DataFrame(
            {
                "column": missing.index,
                "missing_count": missing.values,
                "missing_pct": np.where(
                    total > 0, (missing.values / total) * 100, 0.0
                ),
            }
        )
        return summary.sort_values("missing_count", ascending=False).reset_index(
            drop=True
        )

    def _resolve_columns(self, columns: Optional[list[str]]) -> list[str]:
        """Validate and return column list, defaulting to all columns."""
        if columns is None:
            return list(self._df.columns)

        missing = set(columns) - set(self._df.columns)
        if missing:
            raise DataCleanerError(
                f"Columns not found in DataFrame: {sorted(missing)}"
            )
        return columns