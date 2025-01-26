__all__ = ("router",)


from .router import router as profile_router
from fastapi import APIRouter


router = APIRouter(prefix="/profiles", tags=["PROFILES"])

router.include_router(router=profile_router)
