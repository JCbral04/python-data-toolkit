"""Command-line interface for python-data-toolkit."""

from __future__ import annotations

import logging as lg
from pathlib import Path

import click
import pandas as pd

from pdt._logging import configure_logging
from pdt.anomaly_detector import AnomalyDetector
from pdt.data_cleaner import DataCleaner
from pdt.query_optimizer import QueryOptimizer
from pdt.report_generator import ReportGenerator

configure_logging()
_logger = lg.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """Python Data Analysis Toolkit — CLI."""


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--strategy", default="mean", help="Imputation strategy")
@click.option("--columns", help="Comma-separated column names")
@click.option("--output", "-o", help="Output file path")
@click.option("--format", "output_format", default="csv", type=click.Choice(["csv", "xlsx", "parquet"]))
def clean(input_path: str, strategy: str, columns: str | None, output: str | None, output_format: str) -> None:
    """Clean a dataset: handle missing values and remove duplicates."""
    _logger.info("Cleaning %s with strategy=%s", input_path, strategy)

    df = pd.read_csv(input_path)
    cleaner = DataCleaner(df)

    cols = columns.split(",") if columns else None
    cleaner.handle_missing_values(strategy=strategy, columns=cols)  # type: ignore[arg-type]
    cleaner.remove_duplicates()

    if output:
        if output_format == "csv":
            cleaner.to_csv(output)
        elif output_format == "xlsx":
            cleaner.to_excel(output)
        elif output_format == "parquet":
            cleaner.to_parquet(output)
        click.echo(f"Saved cleaned data to {output}")
    else:
        click.echo(cleaner.data.to_csv(index=False))


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--method", default="iqr", type=click.Choice(["iqr", "zscore", "both"]))
@click.option("--columns", help="Comma-separated column names")
@click.option("--output", "-o", help="Output file for anomaly flags")
def detect(input_path: str, method: str, columns: str | None, output: str | None) -> None:
    """Detect anomalies in a dataset."""
    _logger.info("Detecting anomalies in %s with method=%s", input_path, method)

    df = pd.read_csv(input_path)
    detector = AnomalyDetector(df)

    cols = columns.split(",") if columns else None
    flags = detector.detect(method=method, columns=cols)  # type: ignore[arg-type]

    if output:
        flags.to_csv(output, index=False)
        click.echo(f"Saved anomaly flags to {output}")
    else:
        click.echo(flags.to_csv(index=False))


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "markdown"]))
@click.option("--output", "-o", help="Output file path")
def report(input_path: str, output_format: str, output: str | None) -> None:
    """Generate a report from a dataset."""
    _logger.info("Generating %s report for %s", output_format, input_path)

    df = pd.read_csv(input_path)
    generator = ReportGenerator(df)
    report_text = generator.generate(format=output_format)  # type: ignore[arg-type]

    if output:
        Path(output).write_text(report_text, encoding="utf-8")
        click.echo(f"Saved report to {output}")
    else:
        click.echo(report_text)


@cli.command()
@click.argument("query")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "markdown"]))
def analyze(query: str, output_format: str) -> None:
    """Analyze a SQL query statically."""
    _logger.info("Analyzing SQL query")

    optimizer = QueryOptimizer()
    analysis = optimizer.analyze(query)
    report = optimizer.generate_report(analysis, format=output_format)
    click.echo(report)


if __name__ == "__main__":
    cli()
