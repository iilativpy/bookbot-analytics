"""
Tests for analytics service.
"""

import pytest
from src.services.analytics import AnalyticsService


class TestAnalyticsService:
    """Test cases for AnalyticsService."""
    
    def test_compare_with_last_month(self, test_session, sample_bookings):
        """Test month-over-month comparison."""
        service = AnalyticsService(test_session)
        comparison = service.compare_with_last_month()
        
        assert comparison is not None
        assert 'labels' in comparison
        assert 'period1' in comparison
        assert 'period2' in comparison
        assert 'changes' in comparison
    
    def test_compare_with_last_year(self, test_session, sample_bookings):
        """Test year-over-year comparison."""
        service = AnalyticsService(test_session)
        comparison = service.compare_with_last_year()
        
        assert comparison is not None
        assert 'labels' in comparison
        assert 'changes' in comparison
    
    def test_compare_year_to_date(self, test_session, sample_bookings):
        """Test YTD comparison."""
        service = AnalyticsService(test_session)
        comparison = service.compare_year_to_date()
        
        assert comparison is not None
        assert 'labels' in comparison
        assert 'period1' in comparison
        assert 'period2' in comparison
    
    def test_performance_summary(self, test_session, sample_bookings):
        """Test overall performance summary."""
        service = AnalyticsService(test_session)
        summary = service.get_performance_summary()
        
        assert summary is not None
        assert 'current_month' in summary
        assert 'last_month' in summary
        assert 'year_to_date' in summary
        assert 'month_over_month_change' in summary
    
    def test_identify_trends(self, test_session, sample_bookings):
        """Test trend identification."""
        service = AnalyticsService(test_session)
        trends = service.identify_trends(months=6)
        
        assert trends is not None
        assert 'trend' in trends
        
        if trends['trend'] != 'insufficient_data':
            assert 'trend_percentage' in trends
            assert 'best_month' in trends
            assert 'worst_month' in trends
