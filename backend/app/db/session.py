"""
Database connection and session factory.
Supports SQLite by default and PostgreSQL through DATABASE_URL configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

database_url = settings.DATABASE_URL

# Handle potential postgres:// -> postgresql:// URL prefix difference
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes database schema and ensures all tables exist."""
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
