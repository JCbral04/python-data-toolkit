"""
Example: Data cleaning pipeline.
Run: python examples/01_data_cleaning.py
"""

import pandas as pd
import numpy as np
from src import DataCleaner


def main():
    # Create a messy dataset
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Alice", np.nan],
        "age": [25, np.nan, 30, 25, 28],
        "salary": [50000.0, 60000.0, np.nan, 50000.0, 55000.0],
        "department": ["IT", "HR", "IT", "IT", "HR"],
    })

    print("=== Original Data ===")
    print(df)
    print(f"\nMissing values:\n{df.isna().sum()}")

    # Clean
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values(strategy="mean", columns=["age", "salary"])
    cleaner.remove_duplicates(keep="first")
    cleaner.convert_types({"age": "int64"})

    clean_df = cleaner.data

    print("\n=== Cleaned Data ===")
    print(clean_df)
    print(f"\nMissing values after cleaning:\n{clean_df.isna().sum()}")

    # Export to Excel
    cleaner.to_excel("examples/output_cleaned.xlsx")
    print("\n Saved to examples/output_cleaned.xlsx")


if __name__ == "__main__":
    main()