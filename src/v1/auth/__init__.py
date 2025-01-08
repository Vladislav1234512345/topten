__all__ = ("router",)


from .router import router as auth_router
from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["AUTH"])

router.include_router(router=auth_router)
