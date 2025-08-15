from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import Link, Visit


class LinkRepo:
    @classmethod
    async def create(
        cls, url: str, code: str, session: AsyncSession, commit=True
    ) -> Link:
        link = Link(target=url, code=code)
        session.add(link)
        await session.flush([link])
        if commit:
            await session.commit()
        return link

    @classmethod
    async def get_by_code(cls, code: str, session: AsyncSession) -> Link | None:
        result = await session.execute(select(Link).where(Link.code == code))
        return result.scalar_one_or_none()


class VisitRepo:
    @classmethod
    async def create(cls, link_id: int, session: AsyncSession, commit=True) -> Visit:
        visit = Visit(link_id=link_id)
        session.add(visit)
        await session.flush([visit])
        if commit:
            await session.commit()
        return visit
