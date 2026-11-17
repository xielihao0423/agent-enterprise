from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.agents import router as agents_router
from app.api.v1.models import router as models_router
from app.api.v1.skills import router as skills_router
from app.api.v1.knowledge_bases import router as kb_router
from app.api.v1.memory import router as memory_router
from app.api.v1.feishu_bots import router as feishu_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/api/v1")
api_router.include_router(agents_router, prefix="/api/v1")
api_router.include_router(models_router, prefix="/api/v1")
api_router.include_router(skills_router, prefix="/api/v1")
api_router.include_router(kb_router, prefix="/api/v1")
api_router.include_router(memory_router, prefix="/api/v1")
api_router.include_router(feishu_router, prefix="/api/v1")
api_router.include_router(sessions_router, prefix="/api/v1")
api_router.include_router(audit_router, prefix="/api/v1")
