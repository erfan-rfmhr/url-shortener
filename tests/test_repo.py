from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.link.models import Link, Visit
from src.link.repo import LinkRepo, VisitRepo


class TestLinkRepo:
    """Test cases for LinkRepo class."""

    @pytest.mark.asyncio
    async def test_create_link(self, db_session: AsyncSession):
        """Test creating a new link."""
        url = "https://example.com/test"
        code = "test123"

        link = await LinkRepo.create(url, code, db_session)

        assert link.id is not None
        assert link.target == url
        assert link.code == code
        assert link.visits_count == 0
        assert isinstance(link.created_at, datetime)

    @pytest.mark.asyncio
    async def test_get_by_code_existing(self, db_session: AsyncSession):
        """Test getting an existing link by code."""
        # Create a link first
        url = "https://example.com/existing"
        code = "existing123"
        created_link = await LinkRepo.create(url, code, db_session)

        # Get the link by code
        found_link = await LinkRepo.get_by_code(code, db_session)

        assert found_link is not None
        assert found_link.id == created_link.id
        assert found_link.target == url
        assert found_link.code == code

    @pytest.mark.asyncio
    async def test_get_stats_by_code_with_visits(self, db_session: AsyncSession):
        """Test getting link stats with visits."""
        # Create a link
        url = "https://example.com/stats"
        code = "stats123"
        link = await LinkRepo.create(url, code, db_session)

        # Create some visits
        visit1 = Visit(link_id=link.id)
        visit2 = Visit(link_id=link.id, utm="utm_source=test")
        visit3 = Visit(link_id=link.id)

        db_session.add_all([visit1, visit2, visit3])
        await db_session.commit()

        # Get stats
        stats = await LinkRepo.get_stats_by_code(code, db_session)

        assert stats is not None
        assert stats["id"] == link.id
        assert stats["target"] == url
        assert stats["code"] == code
        assert stats["visit_count"] == 3
        assert isinstance(stats["created_at"], datetime)

    @pytest.mark.asyncio
    async def test_update_visits_count(self, db_session: AsyncSession):
        """Test updating visits count."""
        # Create a link
        link = await LinkRepo.create(
            "https://example.com/count", "count123", db_session
        )
        initial_count = link.visits_count or 0

        # Update visits count
        await LinkRepo.update_visits_count(link.id, db_session)

        # Get updated count
        updated_count = await LinkRepo.get_constant_visits_count(link.id, db_session)
        assert updated_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_update_visits_count_multiple_times(self, db_session: AsyncSession):
        """Test updating visits count multiple times."""
        # Create a link
        link = await LinkRepo.create(
            "https://example.com/multi", "multi123", db_session
        )

        # Update visits count multiple times
        for _ in range(5):
            await LinkRepo.update_visits_count(link.id, db_session)

        # Get final count
        final_count = await LinkRepo.get_constant_visits_count(link.id, db_session)
        assert final_count == 5


class TestVisitRepo:
    """Test cases for VisitRepo class."""

    @pytest.mark.asyncio
    async def test_create_visit(self, db_session: AsyncSession, sample_link: Link):
        """Test creating a new visit."""
        visit = await VisitRepo.create(sample_link.id, db_session)

        assert visit.id is not None
        assert visit.link_id == sample_link.id
        assert visit.utm is None
        assert isinstance(visit.visited_at, datetime)
