__all__ = ("router",)


from .router import router as sms_router
from fastapi import APIRouter


router = APIRouter(prefix="/sms", tags=["SMS"])

router.include_router(router=sms_router)
