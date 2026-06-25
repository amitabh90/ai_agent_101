import pytest
from src.analysis.code_quality import CodeQualityAnalyzer


def test_analyze_diff_no_changes():
    analyzer = CodeQualityAnalyzer()
    
    results = analyzer.analyze_diff("", [])
    
    assert results["files_changed"] == 0
    assert results["lines_added"] == 0
    assert results["lines_removed"] == 0
    assert results["score"] == 100


def test_analyze_diff_with_changes():
    analyzer = CodeQualityAnalyzer()
    
    file_changes = [
        {
            "filename": "test.py",
            "patch": "+def hello():\n+    print('hello')\n-# old code"
        }
    ]
    
    results = analyzer.analyze_diff("", file_changes)
    
    assert results["files_changed"] == 1
    assert results["lines_added"] > 0
    assert results["lines_removed"] > 0


def test_analyze_complexity():
    analyzer = CodeQualityAnalyzer()
    
    code = """
def hello():
    # This is a comment
    print('hello')
    
    return True
"""
    
    complexity = analyzer.analyze_complexity(code)
    
    assert complexity["total_lines"] > 0
    assert complexity["code_lines"] > 0
    assert complexity["comment_lines"] > 0
    assert complexity["blank_lines"] > 0
