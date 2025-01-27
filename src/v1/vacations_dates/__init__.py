__all__ = ("router",)


from .router import router as vacation_date_router
from fastapi import APIRouter


router = APIRouter(prefix="/vacations-dates", tags=["VACATIONS-DATES"])

router.include_router(router=vacation_date_router)
