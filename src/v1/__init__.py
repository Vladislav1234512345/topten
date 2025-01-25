__all__ = ("router",)


from .jwt import router as jwt_router
from .email import router as email_router
from .auth import router as auth_router
from .admin import router as admin_router
from .stuff import router as stuff_router
from .profile import router as profile_router
from fastapi import APIRouter


router = APIRouter(prefix="/v1")

router.include_router(router=jwt_router)
router.include_router(router=email_router)
router.include_router(router=auth_router)
router.include_router(router=admin_router)
router.include_router(router=stuff_router)
router.include_router(router=profile_router)
