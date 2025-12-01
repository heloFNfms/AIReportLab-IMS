from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class FileType(str, enum.Enum):
    """文件类型枚举 - 值必须与数据库中的枚举值完全匹配"""
    TEMPLATE = "TEMPLATE"
    DATA = "DATA"
    OTHER = "OTHER"


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    # 使用 String 类型存储，避免 SQLAlchemy Enum 的大小写问题
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # OSS相关字段
    is_oss = Column(Boolean, default=False)
    oss_path = Column(String(500), nullable=True)
    oss_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
