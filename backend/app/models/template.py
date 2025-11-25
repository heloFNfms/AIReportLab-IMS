"""
模板数据模型
存储报告模板及其AI分析结果
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class TemplateStatus(str, enum.Enum):
    """模板状态"""
    PENDING = "pending"  # 待分析
    ANALYZING = "analyzing"  # 分析中
    COMPLETED = "completed"  # 分析完成
    FAILED = "failed"  # 分析失败


class Template(Base):
    """报告模板表"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True, comment="关联的文件ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    
    # 模板内容
    content = Column(Text, nullable=True, comment="模板原始内容")
    
    # AI分析结果（JSON格式）
    structure = Column(JSON, nullable=True, comment="模板结构分析结果")
    """
    structure示例：
    {
        "报告名称": "光伏发电分析报告",
        "报告类型": "技术分析报告",
        "章节结构": [
            {"章节名": "摘要", "章节级别": 1, "内容要求": "..."},
            ...
        ],
        "风格要求": "正式、数据驱动",
        "格式规则": {...},
        "数据要求": [...]
    }
    """
    
    # 状态和元数据
    status = Column(Enum(TemplateStatus), default=TemplateStatus.PENDING, comment="分析状态")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True, comment="分析完成时间")
