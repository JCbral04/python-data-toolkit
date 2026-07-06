"""Report generation utilities for data analysis summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional, Union

import numpy as np
import pandas as pd

OutputFormat = Literal["text", "markdown"]


class ReportGeneratorError(Exception):
    """Raised when report generation fails."""


class ReportGenerator:
    """Generate text and Markdown reports from pandas DataFrames.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to summarize in reports.
    title : str, default "Data Analysis Report"
        Report title displayed in headers.

    Examples
    --------
    >>> generator = ReportGenerator(df, title="Sales Report")
    >>> text = generator.generate(format="text")
    >>> generator.save("report.md", format="markdown")
    """

    def __init__(
        self,
        df: pd.DataFrame,
        title: str = "Data Analysis Report",
    ) -> None:
        if not isinstance(df, pd.DataFrame):
            raise ReportGeneratorError(
                f"Expected pandas DataFrame, got {type(df).__name__}."
            )
        if df.empty:
            raise ReportGeneratorError("Input DataFrame is empty.")
        if not title.strip():
            raise ReportGeneratorError("Report title must not be empty.")

        self._df = df.copy()
        self.title = title.strip()
        self._generated_at = datetime.now(timezone.utc)

    @property
    def data(self) -> pd.DataFrame:
        """Return a copy of the source DataFrame."""
        return self._df.copy()

    def generate(
        self,
        format: OutputFormat = "text",
        include_stats: bool = True,
        include_missing: bool = True,
        include_sample: bool = True,
        sample_rows: int = 5,
        extra_sections: Optional[dict[str, str]] = None,
    ) -> str:
        """Generate a report in the specified format.

        Parameters
        ----------
        format : {"text", "markdown"}, default "text"
            Output format.
        include_stats : bool, default True
            Include descriptive statistics for numeric columns.
        include_missing : bool, default True
            Include missing-value summary.
        include_sample : bool, default True
            Include a sample of rows.
        sample_rows : int, default 5
            Number of sample rows to include.
        extra_sections : dict, optional
            Additional section title -> content mappings.

        Returns
        -------
        str
            Formatted report string.

        Raises
        ------
        ReportGeneratorError
            If format is invalid or sample_rows is negative.
        """
        if format not in ("text", "markdown"):
            raise ReportGeneratorError(
                f"Invalid format '{format}'. Choose 'text' or 'markdown'."
            )
        if sample_rows < 0:
            raise ReportGeneratorError("sample_rows must be non-negative.")

        sections: list[tuple[str, str]] = []

        sections.append(self._build_overview(format))
        if include_missing:
            sections.append(self._build_missing_section(format))
        if include_stats:
            sections.append(self._build_stats_section(format))
        if include_sample and sample_rows > 0:
            sections.append(
                self._build_sample_section(format, sample_rows)
            )
        if extra_sections:
            for section_title, content in extra_sections.items():
                sections.append((section_title, content))

        if format == "markdown":
            return self._assemble_markdown(sections)
        return self._assemble_text(sections)

    def save(
        self,
        path: Union[str, Path],
        format: OutputFormat = "markdown",
        **kwargs: Any,
    ) -> Path:
        """Generate and save a report to disk.

        Parameters
        ----------
        path : str or Path
            Output file path.
        format : {"text", "markdown"}, default "markdown"
            Report format.
        **kwargs
            Additional arguments forwarded to :meth:`generate`.

        Returns
        -------
        Path
            Resolved path to the written file.

        Raises
        ------
        ReportGeneratorError
            If the file cannot be written.
        """
        output_path = Path(path)
        content = self.generate(format=format, **kwargs)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise ReportGeneratorError(
                f"Failed to write report to '{output_path}': {exc}"
            ) from exc

        return output_path.resolve()

    def _build_overview(self, fmt: OutputFormat) -> tuple[str, str]:
        """Build dataset overview section."""
        rows, cols = self._df.shape
        memory_mb = self._df.memory_usage(deep=True).sum() / (1024 ** 2)
        dtypes = self._df.dtypes.value_counts().to_dict()

        if fmt == "markdown":
            lines = [
                f"- **Rows:** {rows:,}",
                f"- **Columns:** {cols:,}",
                f"- **Memory usage:** {memory_mb:.2f} MB",
                f"- **Generated (UTC):** {self._generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "**Column types:**",
            ]
            for dtype, count in dtypes.items():
                lines.append(f"- `{dtype}`: {count}")
            return ("Overview", "\n".join(lines))

        lines = [
            f"Rows: {rows:,}",
            f"Columns: {cols:,}",
            f"Memory usage: {memory_mb:.2f} MB",
            f"Generated (UTC): {self._generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Column types:",
        ]
        for dtype, count in dtypes.items():
            lines.append(f"  {dtype}: {count}")
        return ("Overview", "\n".join(lines))

    def _build_missing_section(self, fmt: OutputFormat) -> tuple[str, str]:
        """Build missing-value summary section."""
        missing = self._df.isna().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        total = len(self._df)

        if missing.empty:
            content = "No missing values detected."
            return ("Missing Values", content)

        if fmt == "markdown":
            lines = [
                "| Column | Missing | Percent |",
                "|--------|---------|---------|",
            ]
            for col, count in missing.items():
                pct = (count / total) * 100
                lines.append(f"| {col} | {count:,} | {pct:.1f}% |")
            return ("Missing Values", "\n".join(lines))

        lines = [f"{'Column':<20} {'Missing':>10} {'Percent':>10}"]
        lines.append("-" * 42)
        for col, count in missing.items():
            pct = (count / total) * 100
            lines.append(f"{col:<20} {count:>10,} {pct:>9.1f}%")
        return ("Missing Values", "\n".join(lines))

    def _build_stats_section(self, fmt: OutputFormat) -> tuple[str, str]:
        """Build descriptive statistics section."""
        numeric = self._df.select_dtypes(include=np.number)
        if numeric.empty:
            return ("Descriptive Statistics", "No numeric columns available.")

        stats = numeric.describe().round(4)

        if fmt == "markdown":
            return ("Descriptive Statistics", stats.to_markdown())
        return ("Descriptive Statistics", stats.to_string())

    def _build_sample_section(
        self, fmt: OutputFormat, n: int
    ) -> tuple[str, str]:
        """Build sample rows section."""
        sample = self._df.head(n)

        if fmt == "markdown":
            return ("Sample Data", sample.to_markdown(index=False))
        return ("Sample Data", sample.to_string(index=False))

    def _assemble_markdown(
        self, sections: list[tuple[str, str]]
    ) -> str:
        """Combine sections into a Markdown document."""
        parts = [f"# {self.title}", ""]
        for title, content in sections:
            parts.extend([f"## {title}", "", content, ""])
        return "\n".join(parts).rstrip() + "\n"

    def _assemble_text(self, sections: list[tuple[str, str]]) -> str:
        """Combine sections into a plain-text document."""
        separator = "=" * 60
        parts = [self.title, separator]
        for title, content in sections:
            parts.extend(["", title, "-" * len(title), content])
        parts.append("")
        return "\n".join(parts)
