from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.link.models import Link, Visit
from src.link.service import ShortenerService, VisitService


class TestShortenerService:
    """Test cases for ShortenerService class."""

    @pytest.mark.asyncio
    async def test_get_short_url(self):
        """Test generating short URL from code."""
        service = ShortenerService()
        short_url = await service.get_short_url("abc123")

        assert short_url == f"{service.DEFAULT_DOMAIN}/abc123"

    @pytest.mark.asyncio
    async def test_generate_short_code(self):
        """Test generating short code from URL."""
        service = ShortenerService()

        with patch("uuid.uuid4") as mock_uuid:
            # Mock UUID to return predictable value
            mock_uuid.return_value.int = 123456789

            code = await service.generate_short_code("https://example.com")

            assert len(code) + 1 == service.length

    @pytest.mark.asyncio
    async def test_create_short_url_with_session(self, db_session: AsyncSession):
        """Test creating short URL with session."""
        service = ShortenerService()

        with patch.object(service, "generate_short_code", return_value="abc123"):
            with patch.object(service, "perform_create") as mock_create:
                mock_create.return_value = Link(
                    id=1, target="https://example.com", code="abc123"
                )

                short_url = await service.create_short_url(
                    "https://example.com", db_session
                )

                assert short_url == f"{service.DEFAULT_DOMAIN}/abc123"
                mock_create.assert_called_once_with(
                    "https://example.com", "abc123", db_session
                )

    @pytest.mark.asyncio
    async def test_perform_create(self, db_session: AsyncSession):
        """Test performing link creation."""
        service = ShortenerService()

        with patch.object(service.repo, "create") as mock_repo_create:
            mock_link = Link(id=1, target="https://example.com", code="test123")
            mock_repo_create.return_value = mock_link

            result = await service.perform_create(
                "https://example.com", "test123", db_session
            )

            assert result == mock_link
            mock_repo_create.assert_called_once_with(
                "https://example.com", "test123", db_session
            )

    @pytest.mark.asyncio
    async def test_get_target_existing_link(
        self, db_session: AsyncSession, sample_link: Link
    ):
        """Test getting target for existing link."""
        service = ShortenerService()

        with patch.object(service.repo, "get_by_code", return_value=sample_link):
            result = await service.get_target("abc123", db_session)

            assert result == sample_link

    @pytest.mark.asyncio
    async def test_get_url_stats(self, db_session: AsyncSession):
        """Test getting URL stats."""
        service = ShortenerService()
        mock_stats = {
            "id": 1,
            "target": "https://example.com",
            "code": "abc123",
            "visit_count": 5,
        }

        with patch.object(service.repo, "get_stats_by_code", return_value=mock_stats):
            result = await service.get_url_stats("abc123", db_session)

            assert result == mock_stats

    @pytest.mark.asyncio
    async def test_update_visits_count(self, db_session: AsyncSession):
        """Test updating visits count."""
        service = ShortenerService()

        with patch.object(service.repo, "update_visits_count") as mock_update:
            await service.update_visits_count(1, db_session)

            mock_update.assert_called_once_with(1, db_session, True)

    @pytest.mark.asyncio
    async def test_get_link_by_code(self, db_session: AsyncSession, sample_link: Link):
        """Test getting link by code."""
        service = ShortenerService()

        with patch.object(service.repo, "get_by_code", return_value=sample_link):
            result = await service.get_link_by_code("abc123", db_session)

            assert result == sample_link


class TestVisitService:
    """Test cases for VisitService class."""

    @pytest.mark.asyncio
    async def test_create_visit(self, db_session: AsyncSession):
        """Test creating a visit."""
        service = VisitService()
        mock_visit = Visit(id=1, link_id=1)

        with patch.object(
            service.repo, "create", return_value=mock_visit
        ) as mock_create:
            result = await service.create_visit(1, db_session)

            assert result == mock_visit
            mock_create.assert_called_once_with(1, db_session, True)
