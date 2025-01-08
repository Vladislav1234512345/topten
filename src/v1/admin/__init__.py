__all__ = ("router",)

from .router import router as admin_router
from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["ADMIN"])

router.include_router(router=admin_router)
