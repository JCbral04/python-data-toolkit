import numpy as np
import pandas as pd
import pytest

from src.data_cleaner import DataCleaner, DataCleanerError


def test_handle_missing_values():
    # arrange
    df = pd.DataFrame({"score": [10.0, 20.0, np.nan, 40.0]})
    cleaner = DataCleaner(df)

    # act
    result = cleaner.handle_missing_values(strategy="mean")

    # assert
    assert result["score"].isna().sum() == 0  # no missing values
    assert result.loc[2, "score"] == pytest.approx(23.333, rel=1e-3)  # NaN filled with mean
    assert result.loc[0, "score"] == 10.0  # Original unchanged
    assert result.loc[1, "score"] == 20.0  # Original unchanged
    assert result.loc[3, "score"] == 40.0  # Original unchanged


def test_handle_missing_values_median():
    """
    Test that missing values are filled with column median.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [10.0, 20.0, np.nan, 40.0, 50.0],  # median = 30.0
        "B": [1, 2, 3, 4, 5],
    })
    cleaner = DataCleaner(df)

    # Act
    result = cleaner.handle_missing_values(strategy="median")

    # Assert
    expected_median = 30.0
    assert result.loc[2, "A"] == expected_median
    assert result["B"].isna().sum() == 0


def test_handle_missing_values_mode():
    """
    Test that missing values are filled with column mode (most frequent value).
    """
    # Arrange
    df = pd.DataFrame({
        "A": ["x", "y", "x", np.nan, "y", "x"],  # mode = "x" (appears 3 times)
        "B": [1, 2, 3, 4, 5, 6],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.handle_missing_values(strategy="mode")
    
    # Assert
    assert result.loc[3, "A"] == "x"  # NaN filled with mode
    assert result["B"].isna().sum() == 0


def test_handle_missing_values_zero():
    """
    Test that missing values are filled with zero (numeric) or empty string (text).
    """
    # Arrange
    df = pd.DataFrame({
        "num": [1.0, np.nan, 3.0],
        "str": ["a", np.nan, "c"],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.handle_missing_values(strategy="zero")
    
    # Assert
    assert result.loc[1, "num"] == 0.0  # numeric → 0
    assert result.loc[1, "str"] == ""   # text → empty string


def test_handle_missing_values_drop():
    """
    Test that rows with missing values are dropped.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1.0, np.nan, 3.0, 4.0],
        "B": [10, 20, 30, 40],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.handle_missing_values(strategy="drop")
    
    # Assert
    assert len(result) == 3          # 1 row dropped
    assert 1 not in result.index     # row with NaN removed
    assert result["A"].isna().sum() == 0  # no missing values left

def test_handle_missing_values_invalid_strategy():
    """
    Test that an invalid strategy raises DataCleanerError.
    """
    # Arrange
    df = pd.DataFrame({"A": [1, 2, 3]})
    cleaner = DataCleaner(df)
    
    # Act & Assert
    with pytest.raises(DataCleanerError, match="Invalid strategy"):
        cleaner.handle_missing_values(strategy="invalid")

def test_handle_missing_values_non_numeric_mean():
    """
    Test that applying 'mean' to a non-numeric column raises DataCleanerError.
    """
    # Arrange
    df = pd.DataFrame({"A": ["a", "b", None]})
    cleaner = DataCleaner(df)
    
    # Act & Assert
    with pytest.raises(DataCleanerError, match="not numeric"):
        cleaner.handle_missing_values(strategy="mean")

def test_remove_duplicates_first():
    """
    Test that remove_duplicates keeps the first occurrence.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 1, 2],
        "B": ["x", "x", "y"],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.remove_duplicates(keep="first")
    
    # Assert
    assert len(result) == 2
    assert result.loc[0, "A"] == 1
    assert result.loc[0, "B"] == "x"

def test_remove_duplicates_last():
    """
    Test that remove_duplicates keeps the last occurrence.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 1, 2],
        "B": ["x", "x", "y"],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.remove_duplicates(keep="last")
    
    # Assert
    assert len(result) == 2
    assert result.loc[1, "A"] == 1
    assert result.loc[1, "B"] == "x"

def test_remove_duplicates_none():
    """
    Test that remove_duplicates drops all duplicate rows.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 1, 2],
        "B": ["x", "x", "y"],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.remove_duplicates(keep="none")
    
    # Assert
    assert len(result) == 1
    assert result.loc[2, "A"] == 2
    assert result.loc[2, "B"] == "y"

def test_convert_types_int():
    """
    Test that a float column is converted to integer.
    """
    # Arrange
    df = pd.DataFrame({"A": [1.0, 2.0, 3.0]})
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.convert_types({"A": "int64"})
    
    # Assert
    assert pd.api.types.is_integer_dtype(result["A"])
    assert result["A"].iloc[0] == 1

def test_convert_types_datetime():
    """
    Test that a string column is converted to datetime.
    """
    # Arrange
    df = pd.DataFrame({"A": ["2024-01-01", "2024-02-01", None]})
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.convert_types({"A": "datetime64[ns]"})
    
    # Assert
    assert pd.api.types.is_datetime64_any_dtype(result["A"])

def test_get_missing_summary_with_missing():
    """
    Test that get_missing_summary returns correct counts and percentages.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1.0, np.nan, 3.0],
        "B": [10, 20, 30],
        "C": [np.nan, np.nan, 3.0],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.get_missing_summary()
    
    # Assert
    assert len(result) == 3  # all columns included
    assert result[result["column"] == "A"]["missing_count"].iloc[0] == 1
    assert result[result["column"] == "B"]["missing_count"].iloc[0] == 0
    assert result[result["column"] == "C"]["missing_count"].iloc[0] == 2

def test_get_missing_summary_no_missing():
    """
    Test that get_missing_summary returns all zeros when no missing values.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
    })
    cleaner = DataCleaner(df)
    
    # Act
    result = cleaner.get_missing_summary()
    
    # Assert
    assert len(result) == 2
    assert result["missing_count"].sum() == 0
    assert result["missing_pct"].sum() == 0.0