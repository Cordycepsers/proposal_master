"""
Database configuration and session management for the Automated RFP system.
"""
import os
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from contextlib import asynccontextmanager

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rfp_system.db")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "sqlite:///./rfp_system.db")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    pool_pre_ping=True,
)

# Create sync engine for migrations and initial setup
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_db() as db:
            # Use db session
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Dependency for FastAPI to get database session.
    
    Usage in FastAPI routes:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            # Use db
    """
    async with get_db() as session:
        yield session


def get_sync_db():
    """Get synchronous database session for migrations and setup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_database():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Close database connections."""
    await async_engine.dispose()


# Database health check
async def check_database_health() -> bool:
    """Check if database is accessible."""
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
            return True
    except Exception:
        return False
