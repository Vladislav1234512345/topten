__all__ = ("router",)


from .router import router as vacation_time_router
from fastapi import APIRouter


router = APIRouter(prefix="/vacations-times", tags=["VACATIONS-TIMES"])

router.include_router(router=vacation_time_router)
