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