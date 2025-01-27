__all__ = ("router",)


from .router import router as activity_router
from fastapi import APIRouter


router = APIRouter(prefix="/activities", tags=["ACTIVITIES"])

router.include_router(router=activity_router)
