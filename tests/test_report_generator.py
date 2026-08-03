import os
import tempfile

import pandas as pd
import pytest

from src.report_generator import ReportGenerator, ReportGeneratorError


def test_generate_text_basic():
    """
    Test that generate() returns a non-empty string in text format.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"],
    })
    generator = ReportGenerator(df)
    
    # Act
    report = generator.generate(format="text")
    
    # Assert
    assert isinstance(report, str)
    assert len(report) > 0
    assert "A" in report
    assert "B" in report


def test_generate_markdown_basic():
    """
    Test that generate() returns a non-empty string in markdown format.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"],
    })
    generator = ReportGenerator(df)
    
    # Act
    report = generator.generate(format="markdown")
    
    # Assert
    assert isinstance(report, str)
    assert len(report) > 0
    assert "#" in report  # Markdown headers


def test_save_to_file():
    """
    Test that save() writes the report to a file.
    """
    # Arrange
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"],
    })
    generator = ReportGenerator(df)
    
    # Act
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        tmp_path = tmp.name
    
    generator.save(tmp_path, format="text")
    
    # Assert
    assert os.path.exists(tmp_path)
    with open(tmp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "A" in content
    assert "B" in content
    
    # Cleanup
    os.remove(tmp_path)

def test_generate_invalid_format():
    """
    Test that generate() raises ReportGeneratorError for invalid format.
    """
    # Arrange
    df = pd.DataFrame({"A": [1, 2, 3]})
    generator = ReportGenerator(df)
    
    # Act & Assert
    with pytest.raises(ReportGeneratorError, match="Invalid format"):
        generator.generate(format="xml")

def test_generate_with_custom_sections():
    """
    Test that generate() includes custom sections when provided.
    """
    # Arrange
    df = pd.DataFrame({"A": [1, 2, 3]})
    generator = ReportGenerator(df)
    custom = {"Notes": "This is a custom note."}
    
    # Act
    report = generator.generate(format="text", extra_sections=custom)
    
    # Assert
    assert "Notes" in report
    assert "This is a custom note." in report