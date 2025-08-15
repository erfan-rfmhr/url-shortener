from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.link.service import SHORTENER_SERVICE, VISIT_SERVICE

from .link.api.v1.routers import router as link_v1_router
from .logger import log_request_info, logger

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
@log_request_info
async def redirect_to_url(
    request: Request, short_code: str, session: AsyncSession = Depends(get_session)
):
    link = await SHORTENER_SERVICE.get_target(short_code, session)
    if not link:
        return JSONResponse(
            content={"detail": "Link not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    try:
        await VISIT_SERVICE.create_visit(link.id, session, commit=False)
        await SHORTENER_SERVICE.update_visits_count(link.id, session, commit=False)
    except Exception as e:
        logger.error(
            msg=f"Error updating visits: {link.id}",
            exc_info=e,
        )
    await session.commit()
    return RedirectResponse(
        url=link.target, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


router.include_router(api_router)
