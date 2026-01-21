"""
SQLAlchemy ORM models for booking database.
These models can be adapted to match your existing MySQL schema.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Enum, Boolean, Text
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class BookingStatus(enum.Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Customer(Base):
    """
    Customer model.
    Adapt field names to match your existing database schema.
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), nullable=True)
    is_return_customer = Column(Boolean, default=False)
    total_bookings = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', email='{self.email}')>"


class Booking(Base):
    """
    Booking model.
    Adapt field names to match your existing database schema.
    
    Common fields to consider adding based on your needs:
    - room_type, property_id, booking_source, payment_status, etc.
    """
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Booking details
    booking_date = Column(DateTime, default=datetime.utcnow, index=True)
    check_in = Column(DateTime, nullable=False, index=True)
    check_out = Column(DateTime, nullable=False)
    
    # Status
    status = Column(
        Enum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Financial
    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Additional information
    number_of_guests = Column(Integer, default=1)
    special_requests = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="bookings")
    
    def __repr__(self):
        return (
            f"<Booking(id={self.id}, customer_id={self.customer_id}, "
            f"status={self.status.value}, total_price={self.total_price})>"
        )
    
    @property
    def nights(self) -> int:
        """Calculate number of nights for the booking."""
        return (self.check_out - self.check_in).days
    
    @property
    def is_cancelled(self) -> bool:
        """Check if booking is cancelled."""
        return self.status == BookingStatus.CANCELLED
    
    @property
    def is_confirmed(self) -> bool:
        """Check if booking is confirmed."""
        return self.status == BookingStatus.CONFIRMED
    
    @property
    def is_completed(self) -> bool:
        """Check if booking is completed."""
        return self.status == BookingStatus.COMPLETED


# Note for adapting to existing schema:
# ========================================
# If your existing database has different table or column names:
# 1. Update __tablename__ to match your table names
# 2. Update Column names to match your schema
# 3. Adjust data types if needed (String lengths, Float vs Decimal, etc.)
# 4. Add any additional fields specific to your booking system
# 5. Update relationships if you have additional tables
#
# Example of adapting to existing schema:
# If your table is named "reservations" instead of "bookings":
#   __tablename__ = "reservations"
# If your column is "reservation_date" instead of "booking_date":
#   reservation_date = Column(DateTime, default=datetime.utcnow, index=True)
