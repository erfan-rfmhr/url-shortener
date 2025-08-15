import string
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.conf import settings
from src.link.models import Link, Visit

from .repo import LinkRepo, VisitRepo


class ShortenerService:
    default_domain = settings.DEFAULT_DOMAIN
    BASE62 = string.ascii_letters + string.digits
    length = settings.SHORT_URL_LENGTH

    def __init__(self, repo=LinkRepo):
        self.repo = repo

    async def create_short_url(
        self, url: str, session: AsyncSession | None = None
    ) -> str:
        code = await self.generate_short_code(url)
        if session:
            await self.perform_create(url, code, session)
        return f"{self.default_domain}/{code}"

    async def perform_create(self, url: str, code: str, session: AsyncSession) -> Link:
        link = await self.repo.create(url, code, session)
        return link

    async def generate_short_code(self, url: str):
        u = uuid.uuid4()
        short = await self.base62_encode(u.int)
        short = short[: self.length]
        return short

    async def base62_encode(self, num: int) -> str:
        if num == 0:
            return self.BASE62[0]
        encoded = ""
        base = len(self.BASE62)
        while num > 0:
            num, rem = divmod(num, base)
            encoded = self.BASE62[rem] + encoded
        return encoded

    async def get_target(self, short_code: str, session: AsyncSession) -> Link | None:
        link = await self.repo.get_by_code(short_code, session)
        if not link:
            return None
        return link

    async def get_url_stats(
        self, short_code: str, session: AsyncSession
    ) -> dict | None:
        stats = await self.repo.get_stats_by_code(short_code, session)
        return stats

    async def update_visits_count(
        self, link_id: int, session: AsyncSession, commit=True
    ) -> Link:
        link = await self.repo.update_visits_count(link_id, session, commit)
        return link


class VisitService:
    def __init__(self, repo=VisitRepo):
        self.repo = repo

    async def create_visit(
        self, link_id: int, session: AsyncSession, commit=True
    ) -> Visit:
        visit = await self.repo.create(link_id, session, commit)
        return visit


SHORTENER_SERVICE = ShortenerService()

VISIT_SERVICE = VisitService()
