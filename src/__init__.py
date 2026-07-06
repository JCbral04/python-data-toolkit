"""Python Data Analysis Toolkit — production utilities for cleaning, anomaly detection, reporting, and SQL analysis."""

__version__ = "1.0.0"
__author__ = "Python Data Toolkit Team"

from src.anomaly_detector import AnomalyDetector
from src.data_cleaner import DataCleaner
from src.query_optimizer import QueryOptimizer
from src.report_generator import ReportGenerator

__all__ = [
    "__version__",
    "__author__",
    "DataCleaner",
    "AnomalyDetector",
    "ReportGenerator",
    "QueryOptimizer",
]
