"""
Database configuration and session management
"""

import logging
import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Database configuration from environment variables
AUTH_DB_HOST = os.getenv("AUTH_DB_HOST", "auth-db")
AUTH_DB_PORT = os.getenv("AUTH_DB_PORT", "5432")
AUTH_DB_NAME = os.getenv("AUTH_DB_NAME", "stack_builder_auth")
AUTH_DB_USER = os.getenv("AUTH_DB_USER", "stack_builder")
AUTH_DB_PASSWORD = os.getenv("AUTH_DB_PASSWORD", "changeme")

# Construct database URL
DATABASE_URL = os.getenv(
    "AUTH_DATABASE_URL",
    f"postgresql://{AUTH_DB_USER}:{AUTH_DB_PASSWORD}@{AUTH_DB_HOST}:{AUTH_DB_PORT}/{AUTH_DB_NAME}",
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection pool pre-ping to check connections
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    Usage:
        with get_db_context() as db:
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        # Import all models here to ensure they're registered with Base
        from models import (AuditLog, MFABackupCode, RefreshToken, User,
                            UserSettings, UserStack)

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def check_db_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
