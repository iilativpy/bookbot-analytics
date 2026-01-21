"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.database.models import Base, Booking, Customer, BookingStatus


@pytest.fixture(scope="function")
def test_db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_db_engine):
    """Create test database session."""
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def sample_customers(test_session: Session):
    """Create sample customers for testing."""
    customers = [
        Customer(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            is_return_customer=False,
            total_bookings=1
        ),
        Customer(
            id=2,
            name="Jane Smith",
            email="jane@example.com",
            phone="+1234567891",
            is_return_customer=True,
            total_bookings=3
        ),
        Customer(
            id=3,
            name="Bob Johnson",
            email="bob@example.com",
            phone="+1234567892",
            is_return_customer=False,
            total_bookings=1
        ),
    ]
    
    for customer in customers:
        test_session.add(customer)
    test_session.commit()
    
    return customers


@pytest.fixture(scope="function")
def sample_bookings(test_session: Session, sample_customers):
    """Create sample bookings for testing."""
    now = datetime.now()
    bookings = [
        # Current month - confirmed
        Booking(
            id=1,
            customer_id=1,
            booking_date=now,
            check_in=now + timedelta(days=7),
            check_out=now + timedelta(days=10),
            status=BookingStatus.CONFIRMED,
            total_price=500.00,
            number_of_guests=2
        ),
        # Current month - cancelled
        Booking(
            id=2,
            customer_id=2,
            booking_date=now - timedelta(days=5),
            check_in=now + timedelta(days=14),
            check_out=now + timedelta(days=17),
            status=BookingStatus.CANCELLED,
            total_price=750.00,
            number_of_guests=3,
            cancelled_at=now - timedelta(days=2)
        ),
        # Last month - completed
        Booking(
            id=3,
            customer_id=2,
            booking_date=now - timedelta(days=40),
            check_in=now - timedelta(days=35),
            check_out=now - timedelta(days=32),
            status=BookingStatus.COMPLETED,
            total_price=600.00,
            number_of_guests=2
        ),
        # Current month - confirmed
        Booking(
            id=4,
            customer_id=3,
            booking_date=now - timedelta(days=10),
            check_in=now + timedelta(days=5),
            check_out=now + timedelta(days=8),
            status=BookingStatus.CONFIRMED,
            total_price=450.00,
            number_of_guests=2
        ),
    ]
    
    for booking in bookings:
        test_session.add(booking)
    test_session.commit()
    
    return bookings
