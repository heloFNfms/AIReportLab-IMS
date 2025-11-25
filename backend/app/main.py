from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
import os

# 创建上传目录
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(
    title="AIReportLab IMS API",
    description="用户信息管理系统API",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "欢迎使用AIReportLab IMS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
