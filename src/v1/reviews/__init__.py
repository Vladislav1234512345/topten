__all__ = ("router",)


from .router import router as review_router
from fastapi import APIRouter


router = APIRouter(prefix="/reviews", tags=["REVIEWS"])

router.include_router(router=review_router)
