"""
草稿/报告数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class DraftStatus(str, enum.Enum):
    """草稿状态"""
    DRAFT = "draft"
    COMPLETED = "completed"


class Draft(Base):
    """草稿/报告表"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    data_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String(20), default="draft")
    current_version = Column(Integer, default=1)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    versions = relationship("DraftVersion", back_populates="draft", cascade="all, delete-orphan")


class DraftVersion(Base):
    """草稿版本历史表"""
    __tablename__ = "draft_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    change_summary = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    draft = relationship("Draft", back_populates="versions")
