# Python Data Analysis Toolkit

A production-ready Python library for data cleaning, anomaly detection, report generation, and SQL query analysis. Built on **pandas** and **numpy**, it provides typed, well-documented APIs suitable for pipelines, notebooks, and automated reporting workflows.

## Features

| Module | Class | Purpose |
|--------|-------|---------|
| `data_cleaner` | `DataCleaner` | Missing-value imputation, duplicate removal, type conversion |
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
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data_cleaner.py
│   ├── anomaly_detector.py
│   ├── report_generator.py
│   └── query_optimizer.py
└── tests/
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
| `DataCleaner` | 14 | :white_check_mark: Complete |
| `AnomalyDetector` | 7 | :white_check_mark: Complete |
| `ReportGenerator` | 5 | :white_check_mark: Complete |
| `QueryOptimizer` | 6 | :white_check_mark: Complete |
| **Total** | **32** | :white_check_mark: **All passing** |

### Tested Scenarios

**DataCleaner:**
- `handle_missing_values`: mean, median, mode, zero, drop strategies
- Error handling: invalid strategy, non-numeric mean/median
- `remove_duplicates`: first, last, none
- `convert_types`: int64, datetime64
- `get_missing_summary`: with and without missing values

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

## Design Principles

- **Immutable outputs:** Public methods return copies; internal state is updated only through explicit method calls.
- **Type hints:** Full annotations for IDE support and static analysis.
- **Docstrings:** NumPy-style documentation on all public classes and methods.
- **Fail fast:** Clear error messages with actionable context.
- **Test-driven:** 32 unit tests covering all modules and edge cases.

## Author

**Juan Esteban Cabral Bautista**  
*Python Data Toolkit Team*

---

**Version:** 1.0.0
