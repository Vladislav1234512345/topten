__all__ = ("router",)


from .router import router as card_router
from fastapi import APIRouter


router = APIRouter(prefix="/cards", tags=["CARDS"])

router.include_router(router=card_router)
