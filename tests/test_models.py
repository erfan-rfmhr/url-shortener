from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.link.models import Link, Visit


class TestLinkModel:
    """Test cases for Link model."""

    @pytest.mark.asyncio
    async def test_link_creation(self, db_session: AsyncSession):
        """Test Link model database operations."""
        # Create a link
        link = Link(target="https://test.example.com", code="test123")
        db_session.add(link)
        await db_session.commit()
        await db_session.refresh(link)

        # Verify the link was saved
        assert link.id is not None
        assert link.target == "https://test.example.com"
        assert link.code == "test123"
        assert link.visits_count == 0
        assert isinstance(link.created_at, datetime)

    @pytest.mark.asyncio
    async def test_link_unique_code_constraint(self, db_session: AsyncSession):
        """Test that link codes must be unique."""
        # Create first link
        link1 = Link(target="https://example1.com", code="unique123")
        db_session.add(link1)
        await db_session.commit()

        # Try to create second link with same code
        link2 = Link(target="https://example2.com", code="unique123")
        db_session.add(link2)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_link_relationship_with_visits(self, db_session: AsyncSession):
        """Test Link model relationship with Visit model."""
        # Create a link
        link = Link(target="https://example.com", code="rel123")
        db_session.add(link)
        await db_session.commit()
        await db_session.refresh(link)

        # Create visits for the link
        visit1 = Visit(link_id=link.id)
        visit2 = Visit(link_id=link.id, utm="utm_source=test")

        db_session.add_all([visit1, visit2])
        await db_session.commit()

        # Refresh and check relationship
        await db_session.refresh(link)
        assert len(link.visits) == 2
        assert all(visit.link_id == link.id for visit in link.visits)


class TestVisitModel:
    """Test cases for Visit model."""

    @pytest.mark.asyncio
    async def test_visit_creation(self, db_session: AsyncSession, sample_link: Link):
        """Test Visit model database operations."""
        # Create a visit
        visit = Visit(link_id=sample_link.id, utm="utm_source=test")
        db_session.add(visit)
        await db_session.commit()
        await db_session.refresh(visit)

        # Verify the visit was saved
        assert visit.id is not None
        assert visit.link_id == sample_link.id
        assert visit.utm == "utm_source=test"
        assert isinstance(visit.visited_at, datetime)
