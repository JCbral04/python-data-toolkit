"""SQL query analysis and optimization utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


class QueryOptimizerError(Exception):
    """Raised when query analysis fails."""


@dataclass
class QueryAnalysis:
    """Structured result of SQL query analysis.

    Attributes
    ----------
    query : str
        Normalized query string.
    tables : list of str
        Referenced table names.
    columns : list of str
        Selected column names (best-effort extraction).
    has_select_star : bool
        Whether the query uses SELECT *.
    has_where : bool
        Whether a WHERE clause is present.
    has_join : bool
        Whether JOIN clauses are present.
    join_count : int
        Number of JOIN operations detected.
    has_group_by : bool
        Whether GROUP BY is used.
    has_order_by : bool
        Whether ORDER BY is used.
    has_limit : bool
        Whether LIMIT/TOP is used.
    warnings : list of str
        Performance or style warnings.
    suggestions : list of str
        Optimization suggestions.
    estimated_complexity : str
        Rough complexity rating: low, medium, or high.
    """

    query: str
    tables: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    has_select_star: bool = False
    has_where: bool = False
    has_join: bool = False
    join_count: int = 0
    has_group_by: bool = False
    has_order_by: bool = False
    has_limit: bool = False
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    estimated_complexity: str = "low"


class QueryOptimizer:
    """Analyze SQL queries and suggest performance improvements.

    Performs static analysis on SQL strings without requiring a live
    database connection. Useful for code review and query linting.

    Examples
    --------
    >>> optimizer = QueryOptimizer()
    >>> analysis = optimizer.analyze("SELECT * FROM orders WHERE status = 'open'")
    >>> report = optimizer.generate_report(analysis)
    """

    _SELECT_STAR_PATTERN = re.compile(
        r"SELECT\s+\*", re.IGNORECASE
    )
    _FROM_TABLE_PATTERN = re.compile(
        r"\bFROM\s+([`\"\[]?[\w.]+[`\"\]]?)", re.IGNORECASE
    )
    _JOIN_PATTERN = re.compile(
        r"\b(?:INNER|LEFT|RIGHT|FULL|CROSS)?\s*JOIN\s+([`\"\[]?[\w.]+[`\"\]]?)",
        re.IGNORECASE,
    )
    _SELECT_COLUMNS_PATTERN = re.compile(
        r"SELECT\s+(.*?)\s+FROM", re.IGNORECASE | re.DOTALL
    )
    _WHERE_PATTERN = re.compile(r"\bWHERE\b", re.IGNORECASE)
    _GROUP_BY_PATTERN = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)
    _ORDER_BY_PATTERN = re.compile(r"\bORDER\s+BY\b", re.IGNORECASE)
    _LIMIT_PATTERN = re.compile(
        r"\b(?:LIMIT|TOP\s+\d+)\b", re.IGNORECASE
    )
    _SUBQUERY_PATTERN = re.compile(
        r"\(\s*SELECT\b", re.IGNORECASE
    )

    def analyze(self, query: str) -> QueryAnalysis:
        """Analyze a SQL query and return structured findings.

        Parameters
        ----------
        query : str
            SQL query string to analyze.

        Returns
        -------
        QueryAnalysis
            Structured analysis with warnings and suggestions.

        Raises
        ------
        QueryOptimizerError
            If query is empty or not a string.
        """
        if not isinstance(query, str):
            raise QueryOptimizerError(
                f"Expected str, got {type(query).__name__}."
            )

        normalized = " ".join(query.split())
        if not normalized.strip():
            raise QueryOptimizerError("Query string is empty.")

        tables = self._extract_tables(normalized)
        columns = self._extract_columns(normalized)
        has_select_star = bool(self._SELECT_STAR_PATTERN.search(normalized))
        has_where = bool(self._WHERE_PATTERN.search(normalized))
        join_matches = self._JOIN_PATTERN.findall(normalized)
        has_join = len(join_matches) > 0
        join_count = len(join_matches)
        has_group_by = bool(self._GROUP_BY_PATTERN.search(normalized))
        has_order_by = bool(self._ORDER_BY_PATTERN.search(normalized))
        has_limit = bool(self._LIMIT_PATTERN.search(normalized))
        has_subquery = bool(self._SUBQUERY_PATTERN.search(normalized))

        warnings: list[str] = []
        suggestions: list[str] = []

        if has_select_star:
            warnings.append("Query uses SELECT * which may retrieve unnecessary columns.")
            suggestions.append(
                "Specify only required columns in the SELECT clause."
            )

        if not has_where and not has_limit and not has_group_by:
            warnings.append(
                "Full table scan likely: no WHERE, LIMIT, or GROUP BY clause."
            )
            suggestions.append(
                "Add a WHERE clause to filter rows, or LIMIT for exploratory queries."
            )

        if join_count > 3:
            warnings.append(
                f"High join count ({join_count}); query may be expensive."
            )
            suggestions.append(
                "Review join order and ensure indexed columns are used in join conditions."
            )

        if has_order_by and not has_limit:
            suggestions.append(
                "ORDER BY without LIMIT sorts the full result set; add LIMIT if only top-N rows are needed."
            )

        if has_subquery:
            suggestions.append(
                "Consider rewriting correlated subqueries as JOINs or CTEs for better readability."
            )

        if has_group_by and not has_where:
            suggestions.append(
                "Filtering before aggregation (WHERE) is usually cheaper than HAVING."
            )

        complexity = self._estimate_complexity(
            join_count=join_count,
            has_subquery=has_subquery,
            has_group_by=has_group_by,
            has_select_star=has_select_star,
        )

        return QueryAnalysis(
            query=normalized,
            tables=tables,
            columns=columns,
            has_select_star=has_select_star,
            has_where=has_where,
            has_join=has_join,
            join_count=join_count,
            has_group_by=has_group_by,
            has_order_by=has_order_by,
            has_limit=has_limit,
            warnings=warnings,
            suggestions=suggestions,
            estimated_complexity=complexity,
        )

    def generate_report(
        self,
        analysis: QueryAnalysis,
        format: str = "text",
    ) -> str:
        """Generate a human-readable report from query analysis.

        Parameters
        ----------
        analysis : QueryAnalysis
            Result from :meth:`analyze`.
        format : {"text", "markdown"}, default "text"
            Output format.

        Returns
        -------
        str
            Formatted analysis report.

        Raises
        ------
        QueryOptimizerError
            If format is invalid or analysis is not a QueryAnalysis instance.
        """
        if not isinstance(analysis, QueryAnalysis):
            raise QueryOptimizerError(
                f"Expected QueryAnalysis, got {type(analysis).__name__}."
            )
        if format not in ("text", "markdown"):
            raise QueryOptimizerError(
                f"Invalid format '{format}'. Choose 'text' or 'markdown'."
            )

        if format == "markdown":
            return self._report_markdown(analysis)
        return self._report_text(analysis)

    def compare_queries(
        self,
        query_a: str,
        query_b: str,
    ) -> dict[str, object]:
        """Compare two queries and highlight structural differences.

        Parameters
        ----------
        query_a : str
            First query.
        query_b : str
            Second query.

        Returns
        -------
        dict
            Keys: ``analysis_a``, ``analysis_b``, ``differences``.
        """
        analysis_a = self.analyze(query_a)
        analysis_b = self.analyze(query_b)

        differences: list[str] = []

        if analysis_a.estimated_complexity != analysis_b.estimated_complexity:
            differences.append(
                f"Complexity: '{analysis_a.estimated_complexity}' vs "
                f"'{analysis_b.estimated_complexity}'"
            )
        if analysis_a.join_count != analysis_b.join_count:
            differences.append(
                f"Join count: {analysis_a.join_count} vs {analysis_b.join_count}"
            )
        if analysis_a.has_select_star != analysis_b.has_select_star:
            differences.append("SELECT * usage differs between queries.")
        if set(analysis_a.tables) != set(analysis_b.tables):
            differences.append(
                f"Tables differ: {analysis_a.tables} vs {analysis_b.tables}"
            )

        return {
            "analysis_a": analysis_a,
            "analysis_b": analysis_b,
            "differences": differences,
        }

    def _extract_tables(self, query: str) -> list[str]:
        """Extract table names from FROM and JOIN clauses."""
        tables: list[str] = []
        for match in self._FROM_TABLE_PATTERN.finditer(query):
            tables.append(self._clean_identifier(match.group(1)))
        for match in self._JOIN_PATTERN.finditer(query):
            tables.append(self._clean_identifier(match.group(1)))
        return list(dict.fromkeys(tables))

    def _extract_columns(self, query: str) -> list[str]:
        """Best-effort extraction of selected column names."""
        match = self._SELECT_COLUMNS_PATTERN.search(query)
        if not match:
            return []

        raw = match.group(1).strip()
        if raw == "*":
            return ["*"]

        parts = [p.strip() for p in raw.split(",")]
        columns: list[str] = []
        for part in parts:
            alias_match = re.search(r"\bAS\s+([`\"\[]?[\w]+[`\"\]]?)$", part, re.IGNORECASE)
            if alias_match:
                columns.append(self._clean_identifier(alias_match.group(1)))
            else:
                token = part.split()[-1]
                columns.append(self._clean_identifier(token))
        return columns

    @staticmethod
    def _clean_identifier(name: str) -> str:
        """Strip quotes and brackets from SQL identifiers."""
        return name.strip("`\"[]")

    @staticmethod
    def _estimate_complexity(
        join_count: int,
        has_subquery: bool,
        has_group_by: bool,
        has_select_star: bool,
    ) -> str:
        """Estimate query complexity as low, medium, or high."""
        score = 0
        score += join_count
        if has_subquery:
            score += 2
        if has_group_by:
            score += 1
        if has_select_star:
            score += 1

        if score <= 1:
            return "low"
        if score <= 4:
            return "medium"
        return "high"

    @staticmethod
    def _report_text(analysis: QueryAnalysis) -> str:
        """Format analysis as plain text."""
        lines = [
            "SQL Query Analysis",
            "=" * 40,
            f"Complexity: {analysis.estimated_complexity}",
            f"Tables: {', '.join(analysis.tables) or 'none detected'}",
            f"Columns: {', '.join(analysis.columns) or 'none detected'}",
            "",
            "Features:",
            f"  SELECT *: {analysis.has_select_star}",
            f"  WHERE: {analysis.has_where}",
            f"  JOINs: {analysis.join_count}",
            f"  GROUP BY: {analysis.has_group_by}",
            f"  ORDER BY: {analysis.has_order_by}",
            f"  LIMIT: {analysis.has_limit}",
        ]

        if analysis.warnings:
            lines.extend(["", "Warnings:"])
            lines.extend(f"  - {w}" for w in analysis.warnings)

        if analysis.suggestions:
            lines.extend(["", "Suggestions:"])
            lines.extend(f"  - {s}" for s in analysis.suggestions)

        lines.extend(["", "Query:", analysis.query])
        return "\n".join(lines)

    @staticmethod
    def _report_markdown(analysis: QueryAnalysis) -> str:
        """Format analysis as Markdown."""
        lines = [
            "# SQL Query Analysis",
            "",
            f"**Estimated complexity:** {analysis.estimated_complexity}",
            "",
            "## Metadata",
            f"- **Tables:** {', '.join(analysis.tables) or 'none detected'}",
            f"- **Columns:** {', '.join(analysis.columns) or 'none detected'}",
            "",
            "## Features",
            f"- SELECT *: `{analysis.has_select_star}`",
            f"- WHERE: `{analysis.has_where}`",
            f"- JOINs: `{analysis.join_count}`",
            f"- GROUP BY: `{analysis.has_group_by}`",
            f"- ORDER BY: `{analysis.has_order_by}`",
            f"- LIMIT: `{analysis.has_limit}`",
        ]

        if analysis.warnings:
            lines.extend(["", "## Warnings"])
            lines.extend(f"- {w}" for w in analysis.warnings)

        if analysis.suggestions:
            lines.extend(["", "## Suggestions"])
            lines.extend(f"- {s}" for s in analysis.suggestions)

        lines.extend(["", "## Query", "", f"```sql", analysis.query, "```"])
        return "\n".join(lines)
