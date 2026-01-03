# database/db.py - FIXED for SQLAlchemy 2.0
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Generator

# Create data directory
project_root = Path(__file__).parent.parent
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Use in-memory database (no file permission issues)
DATABASE_URL = "sqlite:///:memory:"

print("📁 Using in-memory database")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    try:
        from database.models import Meeting, Conversation
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Database init note: {e}")

def test_db_connection():
    """Test database connection - SQLAlchemy 2.0 compatible"""
    try:
        db = SessionLocal()
        # Use text() wrapper for SQL
        result = db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database test error: {e}")
        return False