"""
Tests for validator utilities.
"""

import pytest
from datetime import datetime, timedelta
from src.utils.validators import DateValidator, QueryValidator


class TestDateValidator:
    """Test cases for DateValidator."""
    
    def test_parse_relative_date_this_month(self):
        """Test parsing 'this month'."""
        result = DateValidator.parse_relative_date("this month")
        
        assert result is not None
        start, end = result
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end
    
    def test_parse_relative_date_last_month(self):
        """Test parsing 'last month'."""
        result = DateValidator.parse_relative_date("last month")
        
        assert result is not None
        start, end = result
        assert start < end
    
    def test_parse_relative_date_days(self):
        """Test parsing 'last N days'."""
        result = DateValidator.parse_relative_date("last 30 days")
        
        assert result is not None
        start, end = result
        days_diff = (end - start).days
        assert 29 <= days_diff <= 31  # Account for timing
    
    def test_parse_relative_date_weeks(self):
        """Test parsing 'last N weeks'."""
        result = DateValidator.parse_relative_date("last 2 weeks")
        
        assert result is not None
        start, end = result
        days_diff = (end - start).days
        assert 13 <= days_diff <= 15
    
    def test_parse_absolute_date(self):
        """Test parsing absolute dates."""
        test_cases = [
            "2024-01-15",
            "15/01/2024",
            "01/15/2024",
        ]
        
        for date_str in test_cases:
            result = DateValidator.parse_absolute_date(date_str)
            if result:
                assert isinstance(result, datetime)
    
    def test_validate_date_range_valid(self):
        """Test valid date range."""
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()
        
        assert DateValidator.validate_date_range(start, end) is True
    
    def test_validate_date_range_invalid_order(self):
        """Test invalid date range (end before start)."""
        start = datetime.now()
        end = datetime.now() - timedelta(days=30)
        
        assert DateValidator.validate_date_range(start, end) is False
    
    def test_validate_date_range_too_large(self):
        """Test date range that's too large."""
        start = datetime.now() - timedelta(days=365 * 6)
        end = datetime.now()
        
        assert DateValidator.validate_date_range(start, end) is False


class TestQueryValidator:
    """Test cases for QueryValidator."""
    
    def test_is_command(self):
        """Test command detection."""
        assert QueryValidator.is_command("/start") is True
        assert QueryValidator.is_command("/stats") is True
        assert QueryValidator.is_command("hello") is False
    
    def test_extract_command(self):
        """Test command extraction."""
        cmd, args = QueryValidator.extract_command("/stats monthly")
        
        assert cmd == "stats"
        assert args == "monthly"
    
    def test_extract_command_no_args(self):
        """Test command extraction without arguments."""
        cmd, args = QueryValidator.extract_command("/help")
        
        assert cmd == "help"
        assert args == ""
    
    def test_validate_prediction_days_valid(self):
        """Test valid prediction days."""
        valid, error = QueryValidator.validate_prediction_days(30)
        
        assert valid is True
        assert error is None
    
    def test_validate_prediction_days_too_small(self):
        """Test prediction days too small."""
        valid, error = QueryValidator.validate_prediction_days(0)
        
        assert valid is False
        assert error is not None
    
    def test_validate_prediction_days_too_large(self):
        """Test prediction days too large."""
        valid, error = QueryValidator.validate_prediction_days(100)
        
        assert valid is False
        assert error is not None
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        dirty = "Hello   World  \x00  with   spaces"
        clean = QueryValidator.sanitize_input(dirty)
        
        assert '\x00' not in clean
        assert '  ' not in clean  # Multiple spaces should be reduced
    
    def test_sanitize_input_length_limit(self):
        """Test input length limiting."""
        long_input = "a" * 2000
        result = QueryValidator.sanitize_input(long_input)
        
        assert len(result) <= 1000
    
    def test_extract_numbers(self):
        """Test number extraction."""
        text = "I want to see stats for the last 30 days and next 7 days"
        numbers = QueryValidator.extract_numbers(text)
        
        assert 30 in numbers
        assert 7 in numbers
        assert len(numbers) == 2
    
    def test_contains_keywords(self):
        """Test keyword detection."""
        text = "Show me the booking statistics for last month"
        
        assert QueryValidator.contains_keywords(text, ["booking", "statistics"]) is True
        assert QueryValidator.contains_keywords(text, ["prediction", "forecast"]) is False
