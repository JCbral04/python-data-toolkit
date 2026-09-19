"""
Shared pytest fixtures for the test suite.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """Return a sample DataFrame with mixed data types and missing values."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "score": [10.0, 20.0, np.nan, 40.0, 50.0],
        "category": ["A", "B", "A", np.nan, "B"],
        "active": [True, False, True, True, False],
    })


@pytest.fixture
def numeric_dataframe():
    """Return a numeric-only DataFrame for anomaly detection tests."""
    return pd.DataFrame({
        "x": [1, 2, 3, 4, 100],
        "y": [10, 20, 30, 40, 50],
    })


@pytest.fixture
def clean_numeric_df():
    """Return a clean numeric DataFrame without outliers."""
    return pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [10, 20, 30, 40, 50],
    })