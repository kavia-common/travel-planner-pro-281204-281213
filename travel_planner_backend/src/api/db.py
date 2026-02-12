"""
Database connection and session management for the Travel Planner backend.

Uses environment variables (configured in .env) to build a PostgreSQL URL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


@dataclass(frozen=True)
class DbConfig:
    """Database config read from environment variables."""

    postgres_url: str


def _get_db_config() -> DbConfig:
    """
    Load DB configuration from environment variables.

    Environment variables expected (already present in backend .env in this template):
    - POSTGRES_URL

    Returns:
        DbConfig: database configuration
    """
    postgres_url = os.getenv("POSTGRES_URL", "").strip().strip('"').strip("'")
    if not postgres_url:
        # Keep error explicit to avoid silent misconfiguration.
        raise RuntimeError("POSTGRES_URL environment variable is required for database connection.")
    return DbConfig(postgres_url=postgres_url)


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""
    cfg = _get_db_config()
    return create_engine(cfg.postgres_url, pool_pre_ping=True)


# Global engine/sessionmaker (simple template approach)
ENGINE = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def get_db_session():
    """
    FastAPI dependency that yields a SQLAlchemy session.

    Yields:
        sqlalchemy.orm.Session: session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
