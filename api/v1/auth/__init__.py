__all__ = ("router", )


from .views import router as views_router
from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["AUTH"])

router.include_router(router=views_router)