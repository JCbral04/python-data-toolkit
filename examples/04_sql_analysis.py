"""
Example: Static SQL query analysis.
Run: python examples/04_sql_analysis.py
"""

from src import QueryOptimizer


def main():
    queries = [
        "SELECT * FROM users WHERE age > 18",
        "SELECT id, name, email FROM orders JOIN customers ON orders.customer_id = customers.id WHERE status = 'completed'",
        "SELECT COUNT(*) FROM products",
    ]

    optimizer = QueryOptimizer()

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")

        analysis = optimizer.analyze(query)
        report = optimizer.generate_report(analysis, format="text")
        print(report)

    # Compare two queries
    print(f"\n{'='*60}")
    print("QUERY COMPARISON")
    print(f"{'='*60}")
    comparison = optimizer.compare_queries(
        "SELECT * FROM large_table",
        "SELECT id FROM large_table WHERE active = 1",
    )
    for key, value in comparison.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()