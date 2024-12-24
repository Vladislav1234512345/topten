__all__ = ("router", )


from .jwt import router as jwt_router
from .sms import router as sms_router
from fastapi import APIRouter


router = APIRouter(prefix="/v1", tags=["V1"])

router.include_router(router=jwt_router)
router.include_router(router=sms_router)
