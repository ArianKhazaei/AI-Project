from fastapi import APIRouter

from backend.api.routes.admin import router as admin_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.registration import router as registration_router
from backend.api.routes.admin_registration import router as admin_registration_router
from backend.api.routes.teacher_prompt import router as teacher_prompt_router
from backend.api.routes.admin_models import router as admin_models_router
from backend.api.routes.lessons import router as lessons_router
from backend.api.routes.students import router as students_router
from backend.api.routes.attempts import router as attempts_router


router = APIRouter()


router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(registration_router)
router.include_router(admin_registration_router)
router.include_router(teacher_prompt_router)
router.include_router(admin_models_router)
router.include_router(lessons_router)
router.include_router(students_router)
router.include_router(attempts_router)
