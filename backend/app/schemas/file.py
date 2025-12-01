from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileBase(BaseModel):
    filename: str
    file_type: str  # 使用字符串类型，避免枚举验证问题


class FileCreate(FileBase):
    pass


class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str  # 使用字符串类型
    file_size: int
    mime_type: Optional[str] = None
    user_id: int
    is_oss: bool = False
    oss_path: Optional[str] = None
    oss_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class FileStatistics(BaseModel):
    total_files: int
    total_templates: int
    total_data_files: int
    total_reports: int  # 生成报告数
