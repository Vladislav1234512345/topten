__all__ = ("router", )


from .v1 import router as v1_router
from fastapi import APIRouter


router = APIRouter(prefix="/api")

router.include_router(router=v1_router)