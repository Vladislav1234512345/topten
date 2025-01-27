__all__ = ("router",)


from .router import router as service_router
from fastapi import APIRouter


router = APIRouter(prefix="/services", tags=["SERVICES"])

router.include_router(router=service_router)
