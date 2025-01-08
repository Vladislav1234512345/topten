__all__ = ("router",)


from .router import router as jwt_router
from fastapi import APIRouter


router = APIRouter(prefix="/jwt", tags=["JWT"])

router.include_router(router=jwt_router)
