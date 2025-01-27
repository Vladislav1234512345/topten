__all__ = ("router",)


from .jwt import router as jwt_router
from .email import router as email_router
from .auth import router as auth_router
from .admin import router as admin_router
from .stuff import router as stuff_router
from .profiles import router as profile_router
from .users import router as user_router
from .cards import router as card_router
from .activities import router as activity_router
from .breaks import router as break_router
from .week_days import router as week_day_router
from .vacations_dates import router as vacation_date_router
from .vacations_times import router as vacation_time_router
from .services import router as service_router
from fastapi import APIRouter


router = APIRouter(prefix="/v1")


router.include_router(router=jwt_router)
router.include_router(router=email_router)
router.include_router(router=auth_router)
router.include_router(router=admin_router)
router.include_router(router=stuff_router)
router.include_router(router=profile_router)
router.include_router(router=user_router)
router.include_router(router=card_router)
router.include_router(router=activity_router)
router.include_router(router=break_router)
router.include_router(router=week_day_router)
router.include_router(router=vacation_date_router)
router.include_router(router=vacation_time_router)
router.include_router(router=service_router)
