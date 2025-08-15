from sqlalchemy import func
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

    @classmethod
    async def get_stats_by_code(cls, code: str, session: AsyncSession) -> dict | None:
        # Get link with visit count
        query = (
            select(
                Link.id,
                Link.target,
                Link.code,
                Link.created_at,
                func.count(Visit.id).label("visit_count"),
            )
            .join(Visit, Link.id == Visit.link_id)
            .where(Link.code == code)
            .group_by(Link.id, Link.target, Link.code, Link.created_at)
        )

        result = await session.execute(query)
        row = result.first()

        if not row:
            return None

        return {
            "id": row.id,
            "target": row.target,
            "code": row.code,
            "created_at": row.created_at,
            "visit_count": row.visit_count,
        }


class VisitRepo:
    @classmethod
    async def create(cls, link_id: int, session: AsyncSession, commit=True) -> Visit:
        visit = Visit(link_id=link_id)
        session.add(visit)
        await session.flush([visit])
        if commit:
            await session.commit()
        return visit
