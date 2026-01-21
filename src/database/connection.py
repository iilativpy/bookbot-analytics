"""
Database connection management with SQLAlchemy.
Supports MySQL with connection pooling.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config import get_config
from .models import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """
    Get or create the SQLAlchemy engine with connection pooling.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        config = get_config()
        
        _engine = create_engine(
            config.database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=config.log_level == "DEBUG",
        )
        
        # Add connection event listeners
        @event.listens_for(_engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")
        
        @event.listens_for(_engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug("Database connection closed")
        
        logger.info("Database engine created successfully")
    
    return _engine


def get_session_factory():
    """
    Get or create the session factory.
    
    Returns:
        sessionmaker: SQLAlchemy session factory
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    return _SessionLocal


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic cleanup.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        with get_session() as session:
            bookings = session.query(Booking).all()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize database tables.
    Note: This creates tables only if they don't exist.
    For existing databases, this is safe to call.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db():
    """Close database connections and dispose engine."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("Database connections closed")
