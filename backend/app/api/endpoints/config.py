from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/config")
def get_config():
    """返回前端特性开关等配置"""
    # 暂时将禁用AI生成功能作为固定开关，也可以通过环境变量控制
    disable_ai = True
    return {
        "featureFlags": {
            "disableAIGeneration": disable_ai
        },
        "uploadFolder": settings.UPLOAD_FOLDER
    }
