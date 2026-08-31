from fastapi import APIRouter

from backend.api.routes.admin_auth import router as admin_auth_router
from backend.api.routes.admin_prompt import router as admin_prompt_router
from backend.api.routes.admin_registration import router as admin_registration_router
from backend.api.routes.admin_users import router as admin_users_router


router = APIRouter()


router.include_router(admin_auth_router)
router.include_router(admin_prompt_router)
router.include_router(admin_registration_router)
router.include_router(admin_users_router)
