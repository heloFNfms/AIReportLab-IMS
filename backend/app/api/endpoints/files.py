from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response
from fastapi.responses import FileResponse as FastAPIFileResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.db.database import get_db
from app.models.user import User
from app.models.file import FileType, File as FileModel
from app.schemas.file import FileResponse, FileStatistics
from app.services.file_service import save_upload_file, get_user_files, get_file_by_id, delete_file, get_file_statistics
from app.services.oss_service import oss_service
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    file_type: FileType = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件到本地存储"""
    return await save_upload_file(file, file_type, current_user.id, db)

@router.post("/upload-oss", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_oss(
    file: UploadFile = File(...),
    file_type: FileType = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件到阿里云OSS"""
    # 上传到OSS
    oss_result = await oss_service.upload_file(file, current_user.id, file_type.value)
    
    # 创建数据库记录
    db_file = FileModel(
        filename=oss_result["original_filename"],
        file_path=oss_result["oss_path"],  # 存储OSS路径
        file_type=file_type,
        file_size=oss_result["file_size"],
        mime_type=oss_result["mime_type"],
        user_id=current_user.id,
        is_oss=True,
        oss_path=oss_result["oss_path"],
        oss_url=oss_result["file_url"]
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@router.get("/", response_model=List[FileResponse])
def get_files(
    file_type: Optional[FileType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有文件"""
    return get_user_files(db, current_user.id, file_type)

@router.get("/statistics", response_model=FileStatistics)
def get_user_file_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户文件统计信息"""
    return get_file_statistics(db, current_user.id)

@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个文件信息"""
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问"
        )
    return file

@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载文件"""
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问"
        )

    # 如果为 OSS 文件，返回签名URL重定向（浏览器将直接下载 OSS 文件）
    if file.is_oss:
        try:
            signed_url = oss_service.get_file_url(file.oss_path)
            return RedirectResponse(url=signed_url, status_code=status.HTTP_302_FOUND)
        except HTTPException:
            raise

    # 本地文件下载
    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    return FastAPIFileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type=file.mime_type or "application/octet-stream"
    )

@router.delete("/{file_id}")
def remove_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文件"""
    return delete_file(db, file_id, current_user.id)
