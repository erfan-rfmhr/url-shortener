import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.config.conf import Settings
from src.link.models import Link, Visit


# Test settings with in-memory SQLite
class TestSettings(Settings):
    DATABASE_URI: str = "sqlite+aiosqlite:///:memory:"
    DEFAULT_DOMAIN: str = "http://test.localhost"
    SHORT_URL_LENGTH: int = 6


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_sessionmaker(test_engine):
    """Create a test session maker."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(test_sessionmaker) -> AsyncGenerator[AsyncSession]:
    """Create a test database session."""
    async with test_sessionmaker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_link(db_session: AsyncSession) -> Link:
    """Create a sample link for testing."""
    link = Link(target="https://example.com", code="abc123", visits_count=0)
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)
    return link


@pytest_asyncio.fixture
async def sample_visit(db_session: AsyncSession, sample_link: Link) -> Visit:
    """Create a sample visit for testing."""
    visit = Visit(link_id=sample_link.id, utm="utm_source=test&utm_medium=test")
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    return visit


@pytest.fixture
def test_settings():
    """Provide test settings."""
    return TestSettings()


# Mock the get_session dependency for integration tests
@pytest.fixture
def override_get_session(db_session):
    """Over_aspytest_asyncioride the get_session dependency for testing."""

    async def _get_session():
        yield db_session

    return _get_session
