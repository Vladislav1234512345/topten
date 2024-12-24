__all__ = ("router", )


from .views import router as views_router
from fastapi import APIRouter


router = APIRouter(prefix="/sms")

router.include_router(router=views_router)