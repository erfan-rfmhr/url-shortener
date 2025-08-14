import string
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.conf import settings
from src.link.models import Link

from .repo import LinkRepo


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

    async def get_target_url(
        self, short_code: str, session: AsyncSession
    ) -> str | None:
        link = await self.repo.get_by_code(short_code, session)
        if not link:
            return None
        return link.target

    async def get_url_stats(self, short_code: str):
        pass


SHORTENER_SERVICE = ShortenerService()
