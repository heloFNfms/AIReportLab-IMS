from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.file import FileType

class FileBase(BaseModel):
    filename: str
    file_type: FileType

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    file_path: str
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
    total_size: int  # 总大小（字节）