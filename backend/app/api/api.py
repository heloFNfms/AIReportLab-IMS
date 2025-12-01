from fastapi import APIRouter
from app.api.endpoints import auth, files

api_router = APIRouter()

# 认证接口
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 文件管理接口
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
