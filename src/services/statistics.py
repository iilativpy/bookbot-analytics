"""
Statistics service for booking data analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from src.database.queries import (
    get_booking_statistics,
    get_return_customer_statistics,
    get_cancellation_details,
    get_monthly_trend_data
)

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for calculating booking statistics."""
    
    def __init__(self, session: Session):
        """
        Initialize statistics service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def get_current_month_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current month.
        
        Returns:
            Dictionary with current month statistics
        """
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        try:
            stats = get_booking_statistics(self.session, start_of_month, now)
            return_stats = get_return_customer_statistics(self.session, start_of_month, now)
            
            return {
                **stats,
                **return_stats,
                "period_label": f"{now.strftime('%B %Y')}"
            }
        except Exception as e:
            logger.error(f"Error getting current month stats: {e}")
            raise
    
    def get_last_month_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the previous month.
        
        Returns:
            Dictionary with last month statistics
        """
        now = datetime.now()
        first_day_current = datetime(now.year, now.month, 1)
        last_day_previous = first_day_current - timedelta(days=1)
        first_day_previous = datetime(last_day_previous.year, last_day_previous.month, 1)
        
        try:
            stats = get_booking_statistics(self.session, first_day_previous, last_day_previous)
            return_stats = get_return_customer_statistics(self.session, first_day_previous, last_day_previous)
            
            return {
                **stats,
                **return_stats,
                "period_label": f"{last_day_previous.strftime('%B %Y')}"
            }
        except Exception as e:
            logger.error(f"Error getting last month stats: {e}")
            raise
    
    def get_year_to_date_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current year to date.
        
        Returns:
            Dictionary with year-to-date statistics
        """
        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)
        
        try:
            stats = get_booking_statistics(self.session, start_of_year, now)
            return_stats = get_return_customer_statistics(self.session, start_of_year, now)
            
            return {
                **stats,
                **return_stats,
                "period_label": f"Year {now.year} (YTD)"
            }
        except Exception as e:
            logger.error(f"Error getting year-to-date stats: {e}")
            raise
    
    def get_custom_period_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for a custom time period.
        
        Args:
            start_date: Start date
            end_date: End date
            label: Optional label for the period
            
        Returns:
            Dictionary with period statistics
        """
        try:
            stats = get_booking_statistics(self.session, start_date, end_date)
            return_stats = get_return_customer_statistics(self.session, start_date, end_date)
            
            period_label = label or f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            
            return {
                **stats,
                **return_stats,
                "period_label": period_label
            }
        except Exception as e:
            logger.error(f"Error getting custom period stats: {e}")
            raise
    
    def get_cancellation_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed cancellation statistics.
        
        Args:
            start_date: Start date (defaults to current month)
            end_date: End date (defaults to now)
            
        Returns:
            Dictionary with cancellation statistics
        """
        if start_date is None:
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
        
        if end_date is None:
            end_date = datetime.now()
        
        try:
            return get_cancellation_details(self.session, start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting cancellation stats: {e}")
            raise
    
    def get_trend_data(self, months: int = 12) -> Dict[str, Any]:
        """
        Get monthly trend data for visualization and analysis.
        
        Args:
            months: Number of months to include
            
        Returns:
            Dictionary with trend data
        """
        try:
            monthly_data = get_monthly_trend_data(self.session, months)
            
            # Calculate summary statistics
            total_bookings = sum(m["bookings"] for m in monthly_data)
            total_revenue = sum(m["revenue"] for m in monthly_data)
            avg_monthly_bookings = total_bookings / len(monthly_data) if monthly_data else 0
            avg_monthly_revenue = total_revenue / len(monthly_data) if monthly_data else 0
            
            return {
                "monthly_data": monthly_data,
                "summary": {
                    "total_bookings": total_bookings,
                    "total_revenue": round(total_revenue, 2),
                    "average_monthly_bookings": round(avg_monthly_bookings, 2),
                    "average_monthly_revenue": round(avg_monthly_revenue, 2),
                    "months_included": len(monthly_data)
                }
            }
        except Exception as e:
            logger.error(f"Error getting trend data: {e}")
            raise
