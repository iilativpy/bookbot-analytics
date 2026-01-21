"""
Complex database queries for booking statistics and analytics.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, and_, or_, extract
from sqlalchemy.orm import Session

from .models import Booking, Customer, BookingStatus

logger = logging.getLogger(__name__)


def get_bookings_by_date_range(
    session: Session,
    start_date: datetime,
    end_date: datetime,
    status: Optional[BookingStatus] = None
) -> List[Booking]:
    """
    Fetch bookings within a date range.
    
    Args:
        session: Database session
        start_date: Start date
        end_date: End date
        status: Optional booking status filter
        
    Returns:
        List of Booking objects
    """
    query = session.query(Booking).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
    )
    
    if status:
        query = query.filter(Booking.status == status)
    
    return query.all()


def get_booking_statistics(
    session: Session,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Get comprehensive booking statistics for a date range.
    
    Args:
        session: Database session
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with statistics
    """
    # Total bookings
    total_bookings = session.query(func.count(Booking.id)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
    ).scalar() or 0
    
    # Bookings by status
    confirmed = session.query(func.count(Booking.id)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.CONFIRMED
        )
    ).scalar() or 0
    
    cancelled = session.query(func.count(Booking.id)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.CANCELLED
        )
    ).scalar() or 0
    
    completed = session.query(func.count(Booking.id)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.COMPLETED
        )
    ).scalar() or 0
    
    # Revenue statistics
    total_revenue = session.query(func.sum(Booking.total_price)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            or_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.status == BookingStatus.COMPLETED
            )
        )
    ).scalar() or 0.0
    
    avg_booking_value = session.query(func.avg(Booking.total_price)).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            or_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.status == BookingStatus.COMPLETED
            )
        )
    ).scalar() or 0.0
    
    # Calculate rates
    booking_rate = (confirmed / total_bookings * 100) if total_bookings > 0 else 0
    cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else 0
    
    return {
        "total_bookings": total_bookings,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "completed": completed,
        "pending": total_bookings - confirmed - cancelled - completed,
        "total_revenue": round(total_revenue, 2),
        "average_booking_value": round(avg_booking_value, 2),
        "booking_rate": round(booking_rate, 2),
        "cancellation_rate": round(cancellation_rate, 2),
        "period_start": start_date,
        "period_end": end_date
    }


def get_return_customer_statistics(
    session: Session,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Calculate return customer statistics.
    
    Args:
        session: Database session
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with return customer stats
    """
    # Get unique customers in period
    customers_in_period = session.query(
        func.count(func.distinct(Booking.customer_id))
    ).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
    ).scalar() or 0
    
    # Get return customers
    return_customers = session.query(
        func.count(func.distinct(Booking.customer_id))
    ).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.customer_id.in_(
                session.query(Booking.customer_id)
                .filter(Booking.created_at < start_date)
                .distinct()
            )
        )
    ).scalar() or 0
    
    return_rate = (return_customers / customers_in_period * 100) if customers_in_period > 0 else 0
    
    return {
        "total_customers": customers_in_period,
        "return_customers": return_customers,
        "new_customers": customers_in_period - return_customers,
        "return_rate": round(return_rate, 2)
    }


def get_daily_booking_counts(
    session: Session,
    start_date: datetime,
    end_date: datetime
) -> List[Tuple[datetime, int]]:
    """
    Get daily booking counts for time series analysis.
    
    Args:
        session: Database session
        start_date: Start date
        end_date: End date
        
    Returns:
        List of (date, count) tuples
    """
    results = session.query(
        func.date(Booking.created_at).label('date'),
        func.count(Booking.id).label('count')
    ).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
    ).group_by(
        func.date(Booking.created_at)
    ).order_by(
        func.date(Booking.created_at)
    ).all()
    
    return [(r.date, r.count) for r in results]


def get_cancellation_details(
    session: Session,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Get detailed cancellation statistics.
    
    Args:
        session: Database session
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with cancellation details
    """
    cancelled_bookings = session.query(Booking).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.CANCELLED
        )
    ).all()
    
    total_cancelled = len(cancelled_bookings)
    lost_revenue = sum(b.total_price for b in cancelled_bookings)
    
    # Calculate average time from booking to cancellation
    cancellation_times = []
    for booking in cancelled_bookings:
        if booking.cancelled_at:
            days_to_cancel = (booking.cancelled_at - booking.created_at).days
            cancellation_times.append(days_to_cancel)
    
    avg_days_to_cancel = (
        sum(cancellation_times) / len(cancellation_times)
        if cancellation_times else 0
    )
    
    # Get cancellation reasons (if available)
    reasons = {}
    for booking in cancelled_bookings:
        if booking.cancellation_reason:
            reason = booking.cancellation_reason
            reasons[reason] = reasons.get(reason, 0) + 1
    
    return {
        "total_cancelled": total_cancelled,
        "lost_revenue": round(lost_revenue, 2),
        "average_days_to_cancel": round(avg_days_to_cancel, 2),
        "cancellation_reasons": reasons
    }


def get_monthly_trend_data(
    session: Session,
    months: int = 12
) -> List[Dict[str, Any]]:
    """
    Get monthly booking trends for the past N months.
    
    Args:
        session: Database session
        months: Number of months to include
        
    Returns:
        List of monthly statistics
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    results = session.query(
        extract('year', Booking.created_at).label('year'),
        extract('month', Booking.created_at).label('month'),
        func.count(Booking.id).label('count'),
        func.sum(Booking.total_price).label('revenue')
    ).filter(
        and_(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
    ).group_by(
        extract('year', Booking.created_at),
        extract('month', Booking.created_at)
    ).order_by(
        extract('year', Booking.created_at),
        extract('month', Booking.created_at)
    ).all()
    
    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "bookings": r.count,
            "revenue": round(float(r.revenue or 0), 2)
        }
        for r in results
    ]


def compare_periods(
    session: Session,
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime
) -> Dict[str, Any]:
    """
    Compare statistics between two time periods.
    
    Args:
        session: Database session
        period1_start: First period start
        period1_end: First period end
        period2_start: Second period start
        period2_end: Second period end
        
    Returns:
        Dictionary with comparison data
    """
    stats1 = get_booking_statistics(session, period1_start, period1_end)
    stats2 = get_booking_statistics(session, period2_start, period2_end)
    
    def calc_change(new_val, old_val):
        if old_val == 0:
            return 100.0 if new_val > 0 else 0.0
        return round(((new_val - old_val) / old_val) * 100, 2)
    
    return {
        "period1": stats1,
        "period2": stats2,
        "changes": {
            "bookings_change": calc_change(stats2["total_bookings"], stats1["total_bookings"]),
            "revenue_change": calc_change(stats2["total_revenue"], stats1["total_revenue"]),
            "booking_rate_change": round(stats2["booking_rate"] - stats1["booking_rate"], 2),
            "cancellation_rate_change": round(stats2["cancellation_rate"] - stats1["cancellation_rate"], 2)
        }
    }
