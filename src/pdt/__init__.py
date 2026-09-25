"""Python Data Analysis Toolkit — production utilities for cleaning, anomaly detection, reporting, and SQL analysis."""

__version__ = "1.0.0"
__author__ = "Python Data Toolkit Team"

from pdt.anomaly_detector import AnomalyDetector
from pdt.data_cleaner import DataCleaner
from pdt.query_optimizer import QueryOptimizer
from pdt.report_generator import ReportGenerator

__all__ = [
    "AnomalyDetector",
    "DataCleaner",
    "QueryOptimizer",
    "ReportGenerator",
    "__author__",
    "__version__",
]
