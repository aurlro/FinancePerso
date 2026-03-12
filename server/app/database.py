"""
Database configuration and connection management
SQLAlchemy 2.0 async support with SQLite
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from .models import Base

# ============================================================================
# Configuration
# ============================================================================

# Default database path - can be overridden via environment
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "Data" / "finance_v6.db"
DB_PATH = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}")

# Create data directory if needed
if DB_PATH.startswith("sqlite"):
    db_file = DB_PATH.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Engine & Session
# ============================================================================

# Create async engine
engine = create_async_engine(
    DB_PATH,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync session for migrations (alembic)
sync_session_maker = sessionmaker(
    bind=engine.sync_engine if hasattr(engine, "sync_engine") else engine,
    expire_on_commit=False,
)


# ============================================================================
# Connection Management
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    Use this for background tasks or when not in FastAPI context.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# Lifecycle
# ============================================================================

async def init_db() -> None:
    """
    Initialize database - create all tables.
    Called at application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections. Called at application shutdown."""
    await engine.dispose()


async def reset_db() -> None:
    """
    Drop and recreate all tables. WARNING: Destroys all data!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
