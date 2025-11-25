"""
报告数据模型
存储AI生成的报告及其元数据
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ReportStatus(str, enum.Enum):
    """报告生成状态"""
    PENDING = "pending"  # 待生成
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 生成完成
    FAILED = "failed"  # 生成失败


class Report(Base):
    """AI生成报告表"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="报告标题")
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, comment="使用的模板ID")
    data_file_id = Column(Integer, ForeignKey("files.id"), nullable=True, comment="数据文件ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    
    # 报告内容（JSON格式，按章节存储）
    content = Column(JSON, nullable=True, comment="报告内容")
    """
    content示例：
    {
        "摘要": "本报告分析了...",
        "方法": "使用了以下数据...",
        "结果与分析": "...",
        "结论": "..."
    }
    """
    
    # 生成的完整文档
    full_text = Column(Text, nullable=True, comment="完整报告文本")
    output_file_id = Column(Integer, ForeignKey("files.id"), nullable=True, comment="生成的文档文件ID")
    
    # 生成参数和元数据
    generation_params = Column(JSON, nullable=True, comment="生成参数")
    """
    generation_params示例：
    {
        "ai_model": "gpt-4o-mini",
        "temperature": 0.7,
        "custom_requirements": "强调数据可视化"
    }
    """
    
    # 状态和进度
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, comment="生成状态")
    progress = Column(Integer, default=0, comment="生成进度（0-100）")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="生成完成时间")
