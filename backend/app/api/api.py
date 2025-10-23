from fastapi import APIRouter
from app.api.endpoints import auth, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(files.router, prefix="/files", tags=["文件"])