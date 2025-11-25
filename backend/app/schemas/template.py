"""
模板相关的Pydantic模型
用于API请求和响应的数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TemplateStructure(BaseModel):
    """模板结构"""
    报告名称: str
    报告类型: str
    章节结构: List[Dict[str, Any]]
    风格要求: str
    格式规则: Dict[str, Any]
    数据要求: Optional[List[str]] = None
    特殊说明: Optional[str] = None


class TemplateCreate(BaseModel):
    """创建模板的请求"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    file_id: Optional[int] = Field(None, description="关联的文件ID")
    content: Optional[str] = Field(None, description="模板内容文本")


class TemplateUpdate(BaseModel):
    """更新模板的请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


class TemplateAnalyzeRequest(BaseModel):
    """模板分析请求"""
    template_id: int = Field(..., description="模板ID")
    force_reanalyze: bool = Field(False, description="是否强制重新分析")


class TemplateResponse(BaseModel):
    """模板响应"""
    id: int
    name: str
    description: Optional[str]
    file_id: Optional[int]
    user_id: int
    content: Optional[str]
    structure: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
