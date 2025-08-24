import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.database import Base
import os

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="session")
def setup_and_teardown_db():
    """Create and drop the test database for the session."""
    from sqlalchemy import create_engine
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+aiosqlite", ""))
    Base.metadata.create_all(bind=sync_engine)
    yield
    os.remove("./test.db")

@pytest_asyncio.fixture(scope="function")
async def db_session(setup_and_teardown_db):
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
