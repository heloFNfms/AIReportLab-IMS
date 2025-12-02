from fastapi import APIRouter
from app.api.endpoints import auth, files, drafts, ai

api_router = APIRouter()

# 认证接口
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 文件管理接口
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])

# 草稿/报告管理接口
api_router.include_router(drafts.router, prefix="/drafts", tags=["报告撰写"])

# AI 辅助接口
api_router.include_router(ai.router, prefix="/ai", tags=["AI辅助"])
