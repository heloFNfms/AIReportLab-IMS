"""
草稿相关的Pydantic模型
用于API请求和响应的数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DraftSaveRequest(BaseModel):
    """保存草稿请求"""
    template_id: int = Field(..., description="模板ID")
    title: Optional[str] = Field(None, description="草稿标题")
    content: str = Field(..., description="草稿内容")
    format: str = Field("markdown", description="内容格式")
    change_summary: Optional[str] = Field(None, description="变更摘要")


class DraftResponse(BaseModel):
    """草稿响应"""
    id: int
    template_id: int
    user_id: int
    title: Optional[str]
    current_version_id: Optional[int]
    editing_stage: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class DraftVersionResponse(BaseModel):
    """草稿版本响应"""
    id: int
    draft_id: int
    version_number: int
    content: str
    format: str
    change_summary: Optional[str]
    word_count: int
    created_at: datetime
    created_by: int
    
    class Config:
        orm_mode = True


class DraftWithContentResponse(BaseModel):
    """带内容的草稿响应（包含当前版本内容）"""
    id: int
    template_id: int
    user_id: int
    title: Optional[str]
    editing_stage: str
    current_version: Optional[DraftVersionResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class DraftVersionListResponse(BaseModel):
    """版本历史列表响应"""
    versions: List[DraftVersionResponse]
    total: int


class EditingStageUpdateRequest(BaseModel):
    """编辑阶段更新请求"""
    editing_stage: str = Field(..., description="编辑阶段: draft/reviewing/completed")
