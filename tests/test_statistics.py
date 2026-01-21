"""
Tests for statistics service.
"""

import pytest
from datetime import datetime, timedelta
from src.services.statistics import StatisticsService


class TestStatisticsService:
    """Test cases for StatisticsService."""
    
    def test_current_month_stats(self, test_session, sample_bookings):
        """Test getting current month statistics."""
        service = StatisticsService(test_session)
        stats = service.get_current_month_stats()
        
        assert stats is not None
        assert 'total_bookings' in stats
        assert 'total_revenue' in stats
        assert 'booking_rate' in stats
        assert 'cancellation_rate' in stats
        
        # Should have 3 bookings in current month (2 confirmed, 1 cancelled)
        assert stats['total_bookings'] == 3
    
    def test_last_month_stats(self, test_session, sample_bookings):
        """Test getting last month statistics."""
        service = StatisticsService(test_session)
        stats = service.get_last_month_stats()
        
        assert stats is not None
        assert 'total_bookings' in stats
        assert 'period_label' in stats
    
    def test_cancellation_stats(self, test_session, sample_bookings):
        """Test cancellation statistics."""
        service = StatisticsService(test_session)
        cancellations = service.get_cancellation_stats()
        
        assert cancellations is not None
        assert 'total_cancelled' in cancellations
        assert 'lost_revenue' in cancellations
        assert cancellations['total_cancelled'] >= 0
    
    def test_trend_data(self, test_session, sample_bookings):
        """Test trend data retrieval."""
        service = StatisticsService(test_session)
        trends = service.get_trend_data(months=6)
        
        assert trends is not None
        assert 'monthly_data' in trends
        assert 'summary' in trends
        assert isinstance(trends['monthly_data'], list)
    
    def test_custom_period_stats(self, test_session, sample_bookings):
        """Test custom period statistics."""
        service = StatisticsService(test_session)
        now = datetime.now()
        start = now - timedelta(days=30)
        
        stats = service.get_custom_period_stats(start, now, "Test Period")
        
        assert stats is not None
        assert stats['period_label'] == "Test Period"
        assert 'total_bookings' in stats


@pytest.mark.parametrize("months,expected_min", [
    (3, 0),
    (6, 0),
    (12, 0),
])
def test_trend_data_months(test_session, sample_bookings, months, expected_min):
    """Test trend data with different month ranges."""
    service = StatisticsService(test_session)
    trends = service.get_trend_data(months=months)
    
    assert len(trends['monthly_data']) >= expected_min
