from fastapi import APIRouter
from app.api.endpoints import auth, files, templates, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(files.router, prefix="/files", tags=["文件"])
api_router.include_router(templates.router, prefix="/templates", tags=["模板管理"])
api_router.include_router(reports.router, prefix="/reports", tags=["报告生成"])