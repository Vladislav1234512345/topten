__all__ = ("router",)


from .router import router as week_day_router
from fastapi import APIRouter


router = APIRouter(prefix="/week-days", tags=["WEEK-DAYS"])

router.include_router(router=week_day_router)
