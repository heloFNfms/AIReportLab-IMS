from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.file import FileType

class FileBase(BaseModel):
    filename: str
    file_type: FileType

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
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

class FilePreviewResponse(BaseModel):
    mime_type: Optional[str] = None
    preview_type: str  # json | csv | text
    content: Optional[Any] = None  # 文本或JSON对象
    csv_rows: Optional[List[List[str]]] = None  # 当预览类型为csv时返回部分行
