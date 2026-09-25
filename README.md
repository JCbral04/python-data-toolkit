# Python Data Analysis Toolkit

[![Tests](https://github.com/JCbral04/python-data-toolkit/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/JCbral04/python-data-toolkit/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/JCbral04/python-data-toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/JCbral04/python-data-toolkit)

A production-ready Python library for data cleaning, anomaly detection, report generation, and SQL query analysis. Built on **pandas** and **numpy**, it provides typed, well-documented APIs suitable for pipelines, notebooks, and automated reporting workflows.

> ⚠️ **Limitation:** `QueryOptimizer` performs static heuristic analysis using regex patterns. It does not parse SQL with a full AST engine. Complex queries (nested CTEs, window functions, or dialect-specific syntax) may produce incomplete results. For production-grade SQL parsing, consider [sqlglot](https://github.com/tobymao/sqlglot).

## Features

| Module | Class | Purpose |
|--------|-------|---------|
| `data_cleaner` | `DataCleaner` | Missing-value imputation, duplicate removal, type conversion, Excel export |
| `anomaly_detector` | `AnomalyDetector` | Outlier detection via IQR and Z-score |
| `report_generator` | `ReportGenerator` | Plain-text and Markdown data summaries |
| `query_optimizer` | `QueryOptimizer` | Static SQL analysis and optimization hints |

## Requirements

- Python 3.9+
- pandas >= 2.0
- numpy >= 1.24
- openpyxl >= 3.1 (Excel I/O support)
- pytest >= 7.4 (testing)
- tabulate >= 0.9.0 (Markdown reports)

## Installation

```bash
git clone https://github.com/JCbral04/python-data-toolkit
cd python-data-toolkit
pip install -r requirements.txt
```

Or install in editable mode:

```bash
pip install -e .
```

## Quick Start

```python
import pandas as pd
from src import DataCleaner, AnomalyDetector, ReportGenerator, QueryOptimizer

# Load data
df = pd.read_csv("data.csv")

# Clean step by step
cleaner = DataCleaner(df)
cleaner.handle_missing_values(strategy="median")
cleaner.remove_duplicates(keep="first")
cleaner.convert_types({"date": "datetime64[ns]", "amount": "float64"})
cleaner.to_excel("output/cleaned_data.xlsx")
cleaned_df = cleaner.data

# Detect anomalies
detector = AnomalyDetector(cleaned_df)
flags = detector.detect(method="both")
anomalies = detector.get_anomaly_rows()

# Generate report
report = ReportGenerator(cleaned_df)
text_report = report.generate(format="text")
report.save("reports/q1_summary.md", format="markdown")

# Analyze SQL
optimizer = QueryOptimizer()
analysis = optimizer.analyze("SELECT * FROM users WHERE age > 18")
report = optimizer.generate_report(analysis, format="text")
print(report)

# Compare two queries
comparison = optimizer.compare_queries(
    "SELECT * FROM orders",
    "SELECT id FROM orders WHERE status = 'completed'"
)
```

## API Reference

### DataCleaner

Handles tabular data preparation.

```python
cleaner = DataCleaner(df)

# Missing values: mean | median | mode | zero | drop
cleaner.handle_missing_values(strategy="median", columns=["revenue"])

# Duplicates: keep first | last | none
cleaner.remove_duplicates(subset=["email"], keep="first")

# Type conversion
cleaner.convert_types({"price": "float64", "created_at": "datetime64[ns]"})

# Export to Excel
cleaner.to_excel("output/data.xlsx", sheet_name="Cleaned")

# Diagnostics
summary = cleaner.get_missing_summary()
```

**Raises:** `DataCleanerError` on invalid input, empty DataFrames, or incompatible strategies.

### AnomalyDetector

Flags outliers using statistical fences.

```python
detector = AnomalyDetector(df)

# method: iqr | zscore | both
flags = detector.detect(columns=["amount"], method="both")
rows = detector.get_anomaly_rows()
summary = detector.get_summary()
```

**Raises:** `AnomalyDetectorError` when no numeric columns exist or parameters are invalid.

### ReportGenerator

Produces structured summaries for stakeholders and logs.

```python
generator = ReportGenerator(df)

text_report = generator.generate(format="text")
md_report = generator.generate(
    format="markdown",
    include_statistics=True,
    include_missing=True,
    sample_rows=10,
)
generator.save("output/report.md", format="markdown")
```

**Raises:** `ReportGeneratorError` on empty data or I/O failures.

### QueryOptimizer

Static SQL linting without a database connection.

```python
optimizer = QueryOptimizer()

analysis = optimizer.analyze("SELECT * FROM users")
report = optimizer.generate_report(analysis, format="text")

comparison = optimizer.compare_queries(query_a, query_b)
```

Returns a `QueryAnalysis` dataclass with tables, columns, feature flags, warnings, suggestions, and an estimated complexity rating.

**Raises:** `QueryOptimizerError` on empty or invalid query strings.

## Project Structure

```
python-data-toolkit/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data_cleaner.py
│   ├── anomaly_detector.py
│   ├── report_generator.py
│   └── query_optimizer.py
└── tests/
    ├── conftest.py
    ├── test_data_cleaner.py
    ├── test_anomaly_detector.py
    ├── test_report_generator.py
    └── test_query_optimizer.py
```

## Error Handling

All modules define domain-specific exceptions:

- `DataCleanerError`
- `AnomalyDetectorError`
- `ReportGeneratorError`
- `QueryOptimizerError`

Input validation runs at construction time and before each operation. Methods return copies of internal state via `.data` properties to prevent unintended mutation.

## Testing

```bash
pytest tests/ -v
```

### Current Coverage

| Module | Tests | Status |
|--------|-------|--------|
| `DataCleaner` | 15 | ✓ Complete |
| `AnomalyDetector` | 7 | ✓ Complete |
| `ReportGenerator` | 5 | ✓ Complete |
| `QueryOptimizer` | 6 | ✓ Complete |
| **Total** | **33** | ✓ **All passing** |

**Code coverage:** 81% ([measured by Codecov](https://codecov.io/gh/JCbral04/python-data-toolkit))

### Tested Scenarios

**DataCleaner:**
- `handle_missing_values`: mean, median, mode, zero, drop strategies
- Error handling: invalid strategy, non-numeric mean/median
- `remove_duplicates`: first, last, none
- `convert_types`: int64, datetime64
- `get_missing_summary`: with and without missing values
- `to_excel`: Excel export with valid file output

**AnomalyDetector:**
- `detect`: IQR, Z-score, both (combined)
- `get_anomaly_rows`: filtering anomalous rows
- `get_summary`: statistical summary
- Error handling: invalid method, no numeric columns

**ReportGenerator:**
- `generate`: text and markdown formats
- `save`: file persistence
- `generate`: custom extra sections
- Error handling: invalid format

**QueryOptimizer:**
- `analyze`: basic SELECT, SELECT * detection, empty query
- `generate_report`: text format
- Error handling: empty query, non-string input, invalid format

# Examples

Runnable scripts demonstrating each module of the toolkit.

## Quick Start

```bash
# All examples assume you're in the project root
cd python-data-toolkit

# 1. Data cleaning
python examples/01_data_cleaning.py

# 2. Anomaly detection
python examples/02_anomaly_detection.py

# 3. Report generation
python examples/03_report_generation.py

# 4. SQL analysis
python examples/04_sql_analysis.py
```

## CLI

Use the toolkit directly from your terminal after installation:

```bash
pip install -e .

# Clean a dataset
pdt clean data.csv --strategy median --output cleaned.csv

# Detect anomalies
pdt detect data.csv --method both --output anomalies.csv

# Generate a report
pdt report data.csv --format markdown --output report.md

# Analyze a SQL query
pdt analyze "SELECT * FROM users WHERE age &gt; 18"

## Design Principles

- **Immutable outputs:** Public methods return copies; internal state is updated only through explicit method calls.
- **Type hints:** Full annotations for IDE support and static analysis.
- **Docstrings:** NumPy-style documentation on all public classes and methods.
- **Fail fast:** Clear error messages with actionable context.
- **Test-driven:** 33 unit tests covering all modules and edge cases.
- **CI/CD:** GitHub Actions runs the full test suite on every push.

## Author

**Juan Esteban Cabral Bautista**  
*Python Data Toolkit Team*

---

**Version:** 1.0.0  
**License:** MIT
