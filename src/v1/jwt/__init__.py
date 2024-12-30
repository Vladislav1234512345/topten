__all__ = ("router", )


from .router import router as views_router
from fastapi import APIRouter


router = APIRouter(prefix="/jwt", tags=["JWT"])

router.include_router(router=views_router)