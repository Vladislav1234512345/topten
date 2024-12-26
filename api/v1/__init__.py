__all__ = ("router", )


from .jwt import router as jwt_router
from .email import router as email_router
from fastapi import APIRouter


router = APIRouter(prefix="/v1")

router.include_router(router=jwt_router)
router.include_router(router=email_router)
