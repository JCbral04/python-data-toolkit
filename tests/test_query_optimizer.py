import pytest

from src.query_optimizer import QueryOptimizer, QueryOptimizerError, QueryAnalysis


def test_analyze_basic_select():
    """
    Test that analyze() detects a simple SELECT query correctly.
    """
    # Arrange
    optimizer = QueryOptimizer()
    query = "SELECT id, name FROM users WHERE active = 1"
    
    # Act
    result = optimizer.analyze(query)
    
    # Assert
    assert isinstance(result, QueryAnalysis)
    assert result.tables == ["users"]
    assert result.columns == ["id", "name"]
    assert result.has_where is True
    assert result.has_select_star is False
    assert result.estimated_complexity == "low"


def test_analyze_select_star_warning():
    """
    Test that SELECT * triggers a warning.
    """
    # Arrange
    optimizer = QueryOptimizer()
    query = "SELECT * FROM orders"
    
    # Act
    result = optimizer.analyze(query)
    
    # Assert
    assert result.has_select_star is True
    assert any("SELECT *" in w for w in result.warnings)
    assert any("Specify only required columns" in s for s in result.suggestions)


def test_analyze_empty_query_error():
    """
    Test that empty query raises QueryOptimizerError.
    """
    # Arrange
    optimizer = QueryOptimizer()
    
    # Act & Assert
    with pytest.raises(QueryOptimizerError, match="empty"):
        optimizer.analyze("")


def test_analyze_non_string_error():
    """
    Test that non-string input raises QueryOptimizerError.
    """
    # Arrange
    optimizer = QueryOptimizer()
    
    # Act & Assert
    with pytest.raises(QueryOptimizerError, match="Expected str"):
        optimizer.analyze(123)


def test_generate_report_text():
    """
    Test that generate_report() returns a non-empty text string.
    """
    # Arrange
    optimizer = QueryOptimizer()
    query = "SELECT id FROM users"
    analysis = optimizer.analyze(query)
    
    # Act
    report = optimizer.generate_report(analysis, format="text")
    
    # Assert
    assert isinstance(report, str)
    assert len(report) > 0
    assert "SQL Query Analysis" in report
    assert "users" in report


def test_generate_report_invalid_format():
    """
    Test that invalid format raises QueryOptimizerError.
    """
    # Arrange
    optimizer = QueryOptimizer()
    query = "SELECT id FROM users"
    analysis = optimizer.analyze(query)
    
    # Act & Assert
    with pytest.raises(QueryOptimizerError, match="Invalid format"):
        optimizer.generate_report(analysis, format="xml")