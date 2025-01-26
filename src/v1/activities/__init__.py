__all__ = ("router",)


from .router import router as user_router
from fastapi import APIRouter


router = APIRouter(prefix="/users", tags=["USERS"])

router.include_router(router=user_router)
