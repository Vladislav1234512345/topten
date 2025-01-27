__all__ = ("router",)


from .router import router as application_router
from fastapi import APIRouter


router = APIRouter(prefix="/applications", tags=["APPLICATIONS"])

router.include_router(router=application_router)
