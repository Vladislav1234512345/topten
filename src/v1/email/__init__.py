__all__ = ("router", )


from .router import router as views_router
from fastapi import APIRouter


router = APIRouter(prefix="/email", tags=["EMAIL"])

router.include_router(router=views_router)