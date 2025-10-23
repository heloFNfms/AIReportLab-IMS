from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/aireport_ims")
    
    # JWT配置
    # ⚠️ 生产环境必须设置 SECRET_KEY 环境变量！
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 文件存储配置
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # 阿里云OSS配置
    # ⚠️ 生产环境必须在 .env 文件中设置这些值！
    OSS_ACCESS_KEY_ID: str = os.getenv("OSS_ACCESS_KEY_ID", "")
    OSS_ACCESS_KEY_SECRET: str = os.getenv("OSS_ACCESS_KEY_SECRET", "")
    OSS_BUCKET_NAME: str = os.getenv("OSS_BUCKET_NAME", "")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
    OSS_URL_PREFIX: str = os.getenv("OSS_URL_PREFIX", "")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()