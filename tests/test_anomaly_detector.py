import numpy as np
import pandas as pd
import pytest

from src.anomaly_detector import AnomalyDetector, AnomalyDetectorError


def test_detect_iqr_basic():
    """
    Test that IQR detection flags clear outliers.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 100],  # 100 is a clear outlier
    })
    detector = AnomalyDetector(df)
    
    # Act
    flags = detector.detect(method="iqr")
    
    # Assert
    assert "A_iqr_anomaly" in flags.columns
    assert flags["A_iqr_anomaly"].dtype == bool
    assert flags.loc[4, "A_iqr_anomaly"] == True   # 100 is outlier
    assert flags.loc[0, "A_iqr_anomaly"] == False  # 1 is not outlier

def test_detect_zscore_basic():
    """
    Test that Z-score detection flags clear outliers.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],  # 100 is far from mean (~14)
    })
    detector = AnomalyDetector(df)
    
    # Act
    flags = detector.detect(method="zscore")
    
    # Assert
    assert "A_zscore_anomaly" in flags.columns
    assert flags["A_zscore_anomaly"].dtype == bool
    assert flags.loc[10, "A_zscore_anomaly"] == True   # 100 is outlier
    assert flags.loc[0, "A_zscore_anomaly"] == False   # 1 is not outlier

def test_detect_both_combined():
    """
    Test that 'both' method returns IQR, Z-score, and combined flags.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
    })
    detector = AnomalyDetector(df)
    
    # Act
    flags = detector.detect(method="both")
    
    # Assert
    assert "A_iqr_anomaly" in flags.columns
    assert "A_zscore_anomaly" in flags.columns
    assert "A_anomaly" in flags.columns  # combined
    
    # 100 should be flagged by both methods
    assert flags.loc[10, "A_iqr_anomaly"] == True
    assert flags.loc[10, "A_zscore_anomaly"] == True
    assert flags.loc[10, "A_anomaly"] == True  # combined = OR
    
    # 1 should not be flagged
    assert flags.loc[0, "A_anomaly"] == False

def test_get_anomaly_rows():
    """
    Test that get_anomaly_rows returns only rows with anomalies.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
        "B": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    })
    detector = AnomalyDetector(df)
    
    # Act
    anomaly_rows = detector.get_anomaly_rows(method="both")
    
    # Assert
    assert len(anomaly_rows) == 1
    assert anomaly_rows.iloc[0]["A"] == 100

def test_get_summary():
    """
    Test that get_summary returns correct anomaly counts.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
    })
    detector = AnomalyDetector(df)
    detector.detect(method="both")
    
    # Act
    summary = detector.get_summary()
    
    # Assert
    assert len(summary) == 3  # iqr, zscore, combined
    combined_row = summary[summary["column"] == "A_anomaly"]
    assert combined_row["anomaly_count"].iloc[0] == 1
    assert combined_row["anomaly_pct"].iloc[0] == pytest.approx(9.09, rel=1e-2)

def test_detect_invalid_method():
    """
    Test that an invalid detection method raises AnomalyDetectorError.
    """
    # Arrange
    df = pd.DataFrame({"A": [1, 2, 3]})
    detector = AnomalyDetector(df)
    
    # Act & Assert
    with pytest.raises(AnomalyDetectorError, match="Invalid method"):
        detector.detect(method="invalid")

def test_detect_no_numeric_columns():
    """
    Test that detect raises error when DataFrame has no numeric columns.
    """
    # Arrange
    df = pd.DataFrame({
        "A": ["a", "b", "c"],
        "B": ["x", "y", "z"],
    })
    detector = AnomalyDetector(df)
    
    # Act & Assert
    with pytest.raises(AnomalyDetectorError, match="No numeric columns"):
        detector.detect()