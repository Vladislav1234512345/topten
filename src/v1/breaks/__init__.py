__all__ = ("router",)


from .router import router as break_router
from fastapi import APIRouter


router = APIRouter(prefix="/breaks", tags=["BREAKS"])

router.include_router(router=break_router)
