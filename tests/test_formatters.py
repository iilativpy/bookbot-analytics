"""
Tests for formatter utilities.
"""

import pytest
from src.utils.formatters import TelegramFormatter


class TestTelegramFormatter:
    """Test cases for TelegramFormatter."""
    
    def test_format_statistics(self):
        """Test statistics formatting."""
        formatter = TelegramFormatter()
        stats = {
            'period_label': 'January 2024',
            'total_bookings': 100,
            'confirmed': 80,
            'cancelled': 10,
            'completed': 60,
            'pending': 10,
            'total_revenue': 50000.00,
            'average_booking_value': 500.00,
            'booking_rate': 80.0,
            'cancellation_rate': 10.0,
            'return_rate': 25.0
        }
        
        result = formatter.format_statistics(stats)
        
        assert isinstance(result, str)
        assert 'January 2024' in result
        assert '100' in result
        assert '50,000' in result or '50000' in result
    
    def test_format_comparison(self):
        """Test comparison formatting."""
        formatter = TelegramFormatter()
        comparison = {
            'labels': {
                'period1': 'December 2023',
                'period2': 'January 2024'
            },
            'changes': {
                'bookings_change': 15.5,
                'revenue_change': 20.0,
                'booking_rate_change': 2.5,
                'cancellation_rate_change': -1.5
            }
        }
        
        result = formatter.format_comparison(comparison)
        
        assert isinstance(result, str)
        assert 'December 2023' in result
        assert 'January 2024' in result
        assert '+15.5' in result or '15.5' in result
    
    def test_format_prediction(self):
        """Test prediction formatting."""
        formatter = TelegramFormatter()
        
        # Successful prediction
        prediction = {
            'success': True,
            'method': 'Prophet',
            'summary': {
                'prediction_period_days': 30,
                'total_predicted_bookings': 150,
                'average_daily_bookings': 5.0,
                'historical_data_days': 90
            }
        }
        
        result = formatter.format_prediction(prediction)
        
        assert isinstance(result, str)
        assert 'Prophet' in result
        assert '30' in result
        assert '150' in result
    
    def test_format_prediction_error(self):
        """Test prediction error formatting."""
        formatter = TelegramFormatter()
        
        prediction = {
            'success': False,
            'error': 'Insufficient data'
        }
        
        result = formatter.format_prediction(prediction)
        
        assert isinstance(result, str)
        assert 'Error' in result or 'error' in result
        assert 'Insufficient data' in result
    
    def test_format_trends(self):
        """Test trends formatting."""
        formatter = TelegramFormatter()
        trends = {
            'trend': 'increasing',
            'trend_percentage': 12.5,
            'average_first_half': 80.0,
            'average_second_half': 90.0,
            'best_month': {'year': 2024, 'month': 1, 'bookings': 120, 'revenue': 60000},
            'worst_month': {'year': 2023, 'month': 7, 'bookings': 50, 'revenue': 25000},
            'total_months_analyzed': 6
        }
        
        result = formatter.format_trends(trends)
        
        assert isinstance(result, str)
        assert 'increasing' in result.lower()
        assert '12.5' in result
    
    def test_format_cancellations(self):
        """Test cancellations formatting."""
        formatter = TelegramFormatter()
        cancellations = {
            'total_cancelled': 15,
            'lost_revenue': 7500.00,
            'average_days_to_cancel': 5.5,
            'cancellation_reasons': {
                'Changed plans': 8,
                'Found cheaper': 4,
                'Other': 3
            }
        }
        
        result = formatter.format_cancellations(cancellations)
        
        assert isinstance(result, str)
        assert '15' in result
        assert '7,500' in result or '7500' in result
    
    def test_format_help(self):
        """Test help message formatting."""
        formatter = TelegramFormatter()
        result = formatter.format_help()
        
        assert isinstance(result, str)
        assert '/stats' in result
        assert '/predict' in result
        assert '/help' in result
    
    def test_format_error(self):
        """Test error message formatting."""
        formatter = TelegramFormatter()
        result = formatter.format_error("Something went wrong")
        
        assert isinstance(result, str)
        assert 'Error' in result
        assert 'Something went wrong' in result
