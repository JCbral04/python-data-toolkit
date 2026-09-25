"""
Example: Generate a Markdown report from a dataset.
Run: python examples/03_report_generation.py
"""

import pandas as pd
from pdt import ReportGenerator


def main():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headset"],
        "price": [999.99, 25.50, 75.00, 299.99, 49.99],
        "stock": [10, 150, 80, 25, 200],
        "category": ["Electronics", "Accessories", "Accessories", "Electronics", "Accessories"],
    })

    generator = ReportGenerator(df)

    # Text report
    text = generator.generate(format="text")
    print("=== TEXT REPORT ===")
    print(text)

    # Markdown report
    md = generator.generate(
        format="markdown",
        include_statistics=True,
        include_missing=True,
        sample_rows=3,
    )
    print("\n=== MARKDOWN REPORT ===")
    print(md)

    # Save to file
    generator.save("examples/output_report.md", format="markdown")
    print("\n Saved to examples/output_report.md")


if __name__ == "__main__":
    main()
