"""
草稿管理数据模型
支持版本历史和编辑阶段追踪
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class EditingStage(str, enum.Enum):
    """编辑阶段枚举"""
    DRAFT = "draft"           # 草稿阶段
    REVIEWING = "reviewing"   # 审阅中
    COMPLETED = "completed"   # 已完成


class Draft(Base):
    """草稿主表"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, comment="模板ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(255), nullable=True, comment="草稿标题")
    
    # 当前版本ID（指向最新版本）
    current_version_id = Column(Integer, ForeignKey("draft_versions.id"), nullable=True, comment="当前版本ID")
    
    # 编辑阶段
    editing_stage = Column(Enum(EditingStage), default=EditingStage.DRAFT, nullable=False, comment="编辑阶段")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    versions = relationship("DraftVersion", back_populates="draft", foreign_keys="DraftVersion.draft_id")


class DraftVersion(Base):
    """草稿版本历史表"""
    __tablename__ = "draft_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False, comment="草稿ID")
    
    # 版本信息
    version_number = Column(Integer, nullable=False, comment="版本号（从1开始）")
    content = Column(Text, nullable=False, comment="版本内容")
    format = Column(String(50), default="markdown", nullable=False, comment="内容格式")
    
    # 元数据
    change_summary = Column(String(500), nullable=True, comment="变更摘要")
    word_count = Column(Integer, default=0, comment="字数统计")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    
    # 关系
    draft = relationship("Draft", back_populates="versions", foreign_keys=[draft_id])
