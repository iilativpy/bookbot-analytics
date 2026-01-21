"""
Analytics service for comparing periods and generating insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from src.database.queries import compare_periods, get_booking_statistics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for advanced analytics and comparisons."""
    
    def __init__(self, session: Session):
        """
        Initialize analytics service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def compare_with_last_month(self) -> Dict[str, Any]:
        """
        Compare current month with last month.
        
        Returns:
            Dictionary with comparison data
        """
        now = datetime.now()
        
        # Current month
        current_start = datetime(now.year, now.month, 1)
        current_end = now
        
        # Last month
        last_month_end = current_start - timedelta(days=1)
        last_month_start = datetime(last_month_end.year, last_month_end.month, 1)
        
        try:
            comparison = compare_periods(
                self.session,
                last_month_start, last_month_end,
                current_start, current_end
            )
            
            comparison["labels"] = {
                "period1": last_month_end.strftime('%B %Y'),
                "period2": now.strftime('%B %Y') + " (current)"
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing with last month: {e}")
            raise
    
    def compare_with_last_year(self) -> Dict[str, Any]:
        """
        Compare current month with same month last year.
        
        Returns:
            Dictionary with year-over-year comparison
        """
        now = datetime.now()
        
        # Current month
        current_start = datetime(now.year, now.month, 1)
        current_end = now
        
        # Same month last year
        last_year_start = datetime(now.year - 1, now.month, 1)
        # Get the last day of that month
        if now.month == 12:
            last_year_end = datetime(now.year, 1, 1) - timedelta(days=1)
        else:
            last_year_end = datetime(now.year - 1, now.month + 1, 1) - timedelta(days=1)
        
        try:
            comparison = compare_periods(
                self.session,
                last_year_start, last_year_end,
                current_start, current_end
            )
            
            comparison["labels"] = {
                "period1": last_year_start.strftime('%B %Y'),
                "period2": now.strftime('%B %Y') + " (current)"
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing with last year: {e}")
            raise
    
    def compare_year_to_date(self) -> Dict[str, Any]:
        """
        Compare current year-to-date with last year same period.
        
        Returns:
            Dictionary with YTD comparison
        """
        now = datetime.now()
        
        # Current YTD
        current_ytd_start = datetime(now.year, 1, 1)
        current_ytd_end = now
        
        # Last year same period
        last_year_ytd_start = datetime(now.year - 1, 1, 1)
        last_year_ytd_end = datetime(now.year - 1, now.month, now.day)
        
        try:
            comparison = compare_periods(
                self.session,
                last_year_ytd_start, last_year_ytd_end,
                current_ytd_start, current_ytd_end
            )
            
            comparison["labels"] = {
                "period1": f"YTD {now.year - 1}",
                "period2": f"YTD {now.year} (current)"
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing YTD: {e}")
            raise
    
    def compare_custom_periods(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
        label1: str = "Period 1",
        label2: str = "Period 2"
    ) -> Dict[str, Any]:
        """
        Compare two custom time periods.
        
        Args:
            period1_start: First period start
            period1_end: First period end
            period2_start: Second period start
            period2_end: Second period end
            label1: Label for first period
            label2: Label for second period
            
        Returns:
            Dictionary with comparison data
        """
        try:
            comparison = compare_periods(
                self.session,
                period1_start, period1_end,
                period2_start, period2_end
            )
            
            comparison["labels"] = {
                "period1": label1,
                "period2": label2
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing custom periods: {e}")
            raise
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary with key metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        now = datetime.now()
        
        try:
            # Current month
            current_month_start = datetime(now.year, now.month, 1)
            current_month_stats = get_booking_statistics(self.session, current_month_start, now)
            
            # Last month
            last_month_end = current_month_start - timedelta(days=1)
            last_month_start = datetime(last_month_end.year, last_month_end.month, 1)
            last_month_stats = get_booking_statistics(self.session, last_month_start, last_month_end)
            
            # YTD
            ytd_start = datetime(now.year, 1, 1)
            ytd_stats = get_booking_statistics(self.session, ytd_start, now)
            
            return {
                "current_month": {
                    "label": now.strftime('%B %Y'),
                    "stats": current_month_stats
                },
                "last_month": {
                    "label": last_month_end.strftime('%B %Y'),
                    "stats": last_month_stats
                },
                "year_to_date": {
                    "label": f"YTD {now.year}",
                    "stats": ytd_stats
                },
                "month_over_month_change": {
                    "bookings": current_month_stats["total_bookings"] - last_month_stats["total_bookings"],
                    "revenue": round(current_month_stats["total_revenue"] - last_month_stats["total_revenue"], 2)
                }
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            raise
    
    def identify_trends(self, months: int = 6) -> Dict[str, Any]:
        """
        Identify booking trends over the past N months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with trend insights
        """
        from src.database.queries import get_monthly_trend_data
        
        try:
            monthly_data = get_monthly_trend_data(self.session, months)
            
            if len(monthly_data) < 2:
                return {
                    "trend": "insufficient_data",
                    "message": "Need at least 2 months of data for trend analysis"
                }
            
            # Calculate trend direction
            first_half = monthly_data[:len(monthly_data)//2]
            second_half = monthly_data[len(monthly_data)//2:]
            
            first_half_avg = sum(m["bookings"] for m in first_half) / len(first_half)
            second_half_avg = sum(m["bookings"] for m in second_half) / len(second_half)
            
            trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing"
            trend_percentage = round(abs((second_half_avg - first_half_avg) / first_half_avg * 100), 2)
            
            # Find best and worst months
            best_month = max(monthly_data, key=lambda x: x["bookings"])
            worst_month = min(monthly_data, key=lambda x: x["bookings"])
            
            return {
                "trend": trend_direction,
                "trend_percentage": trend_percentage,
                "average_first_half": round(first_half_avg, 2),
                "average_second_half": round(second_half_avg, 2),
                "best_month": best_month,
                "worst_month": worst_month,
                "total_months_analyzed": len(monthly_data)
            }
        except Exception as e:
            logger.error(f"Error identifying trends: {e}")
            raise
