from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.link.service import SHORTENER_SERVICE

from .link.api.v1.routers import router as link_v1_router

router = APIRouter()
api_router = APIRouter(prefix="/api")


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(link_v1_router, prefix="/link")

api_router.include_router(v1_router)


@router.get(
    "/{short_code}",
    responses={
        status.HTTP_307_TEMPORARY_REDIRECT: {
            "description": "Temporary redirect to the target URL",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Link not found",
        },
    },
)
async def redirect_to_url(
    short_code: str, request: Request, session: AsyncSession = Depends(get_session)
):
    target_url = await SHORTENER_SERVICE.get_target_url(short_code, session)
    if not target_url:
        return JSONResponse(
            content={"detail": "Link not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return RedirectResponse(
        url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


router.include_router(api_router)
