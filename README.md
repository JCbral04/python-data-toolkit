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
optimizer = QueryOptimizer("SELECT * FROM users WHERE age > 18")
analysis = optimizer.analyze()
print(optimizer.generate_report(format="text"))
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
optimizer = QueryOptimizer("SELECT * FROM users")

analysis = optimizer.analyze()
report = optimizer.generate_report(format="text")

comparison = QueryOptimizer.compare(query_a, query_b)
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
    └── test_data_cleaner.py
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
| `AnomalyDetector` | 0 | :arrows_counterclockwise: Pending |
| `ReportGenerator` | 0 | :arrows_counterclockwise: Pending |
| `QueryOptimizer` | 0 | :arrows_counterclockwise: Pending |

## Design Principles

- **Immutable outputs:** Public methods return copies; internal state is updated only through explicit method calls.
- **Type hints:** Full annotations for IDE support and static analysis.
- **Docstrings:** NumPy-style documentation on all public classes and methods.
- **Fail fast:** Clear error messages with actionable context.

## Author

**Juan Esteban Cabral Bautista**  
*Python Data Toolkit Team*

---

**Version:** 1.0.0
