__all__ = ("router",)


from .router import router as stuff_router
from fastapi import APIRouter


router = APIRouter(prefix='/stuff', tags=['STUFF'])

router.include_router(router=stuff_router)