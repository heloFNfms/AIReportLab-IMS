"""
报告相关的Pydantic模型
用于API请求和响应的数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ReportCreate(BaseModel):
    """创建报告的请求"""
    title: str = Field(..., description="报告标题")
    template_id: int = Field(..., description="使用的模板ID")
    data_file_id: Optional[int] = Field(None, description="数据文件ID")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="生成参数")


class ReportUpdate(BaseModel):
    """更新报告的请求"""
    title: Optional[str] = None
    content: Optional[Dict[str, str]] = None
    full_text: Optional[str] = None


class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    template_id: int = Field(..., description="模板ID")
    data_file_id: Optional[int] = Field(None, description="数据文件ID（可选）")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="自定义数据")
    title: Optional[str] = Field(None, description="报告标题")
    requirements: Optional[str] = Field(None, description="额外要求")
    ai_model: Optional[str] = Field(None, description="指定AI模型")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="生成温度")


class ReportResponse(BaseModel):
    """报告响应"""
    id: int
    title: str
    template_id: int
    data_file_id: Optional[int]
    user_id: int
    content: Optional[Dict[str, str]]
    full_text: Optional[str]
    output_file_id: Optional[int]
    generation_params: Optional[Dict[str, Any]]
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """报告列表响应"""
    id: int
    title: str
    template_id: int
    status: str
    progress: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportStatusResponse(BaseModel):
    """报告生成状态响应"""
    status: str
    progress: int
    error_message: Optional[str]
    completed_at: Optional[datetime]
