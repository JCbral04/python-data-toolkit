"""
Example: Anomaly detection on sales data.
Run: python examples/02_anomaly_detection.py
"""

import pandas as pd
from pdt import AnomalyDetector


def main():
    # Sales data with an obvious outlier
    df = pd.DataFrame({
        "day": range(1, 11),
        "sales": [100, 105, 98, 110, 102, 108, 95, 103, 101, 500],  # 500 is outlier
    })

    print("=== Sales Data ===")
    print(df)

    detector = AnomalyDetector(df)
    flags = detector.detect(method="both")

    print("\n=== Anomaly Flags ===")
    print(flags)

    anomaly_rows = detector.get_anomaly_rows()
    print(f"\n=== Anomalous Rows ({len(anomaly_rows)} found) ===")
    print(anomaly_rows)

    summary = detector.get_summary()
    print("\n=== Summary ===")
    print(summary)


if __name__ == "__main__":
    main()
