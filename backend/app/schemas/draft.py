"""
草稿/报告相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DraftCreate(BaseModel):
    """创建草稿"""
    title: str = Field(..., description="报告标题")
    template_file_id: Optional[int] = Field(None, description="模板文件ID")
    data_file_id: Optional[int] = Field(None, description="数据文件ID")
    content: Optional[str] = Field(None, description="初始内容")


class DraftUpdate(BaseModel):
    """更新草稿"""
    title: Optional[str] = None
    content: Optional[str] = None
    data_file_id: Optional[int] = None
    change_summary: Optional[str] = Field(None, description="变更摘要（用于版本记录）")


class DraftComplete(BaseModel):
    """完成草稿"""
    title: Optional[str] = None
    content: Optional[str] = None


class DraftVersionResponse(BaseModel):
    """版本响应"""
    id: int
    draft_id: int
    version: int
    content: str
    word_count: int
    change_summary: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True


class DraftResponse(BaseModel):
    """草稿响应"""
    id: int
    title: str
    user_id: int
    template_file_id: Optional[int]
    data_file_id: Optional[int]
    content: Optional[str]
    status: str
    current_version: int
    word_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class DraftListResponse(BaseModel):
    """草稿列表响应"""
    id: int
    title: str
    status: str
    current_version: int
    word_count: int
    template_file_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class DraftWithVersionsResponse(DraftResponse):
    """带版本历史的草稿响应"""
    versions: List[DraftVersionResponse] = []
    
    class Config:
        orm_mode = True
