from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.link.service import SHORTENER_SERVICE

from .schemas import ShortenedUrl, TargetUrl, UrlStats

router = APIRouter(
    default_response_class=JSONResponse,
    tags=["link"],
)


@router.post("/shorten", response_model=ShortenedUrl)
async def create_short_url(
    body: TargetUrl, session: AsyncSession = Depends(get_session)
):
    target_url = body.target_url
    if not target_url.startswith("http"):
        target_url = f"https://{target_url}"

    shortened_url = await SHORTENER_SERVICE.create_short_url(target_url, session)
    response_data = ShortenedUrl(shortened_url=shortened_url, target_url=target_url)

    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/stats/{short_code}", response_model=UrlStats)
async def get_url_stats(short_code: str, session: AsyncSession = Depends(get_session)):
    stats = await SHORTENER_SERVICE.get_url_stats(short_code, session)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
        )

    response_data = UrlStats(
        short_code=stats["code"],
        target_url=stats["target"],
        visit_count=stats["visit_count"],
        created_at=stats["created_at"].isoformat(),
    )

    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status.HTTP_200_OK,
    )
