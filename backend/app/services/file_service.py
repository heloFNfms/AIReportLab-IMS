import os
import aiofiles
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.file import File, FileType
from app.schemas.file import FileCreate, FileStatistics
from app.core.config import settings
from app.services.oss_service import oss_service
from typing import List
import uuid

async def save_upload_file(upload_file: UploadFile, file_type: FileType, user_id: int, db: Session):
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    user_folder = os.path.join(settings.UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(user_folder, unique_filename)
    
    # 异步保存文件
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)"
                )
            await out_file.write(content)
    except Exception as e:
        # 如果保存失败，删除可能部分写入的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 创建文件记录
    db_file = File(
        filename=upload_file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        mime_type=upload_file.content_type,
        user_id=user_id
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_user_files(db: Session, user_id: int, file_type: FileType = None):
    query = db.query(File).filter(File.user_id == user_id)
    if file_type:
        query = query.filter(File.file_type == file_type)
    return query.all()

def get_file_by_id(db: Session, file_id: int, user_id: int):
    return db.query(File).filter(File.id == file_id, File.user_id == user_id).first()

def delete_file(db: Session, file_id: int, user_id: int):
    file = get_file_by_id(db, file_id, user_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问"
        )
    
    # 删除物理文件
    try:
        if file.is_oss:
            if file.oss_path:
                ok = oss_service.delete_file(file.oss_path)
                if not ok:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="OSS文件删除失败"
                    )
        else:
            # 如果是本地文件，从本地删除
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )
    
    # 删除数据库记录
    db.delete(file)
    db.commit()
    return {"message": "文件删除成功"}

def get_file_statistics(db: Session, user_id: int) -> FileStatistics:
    files = get_user_files(db, user_id)
    total_files = len(files)
    total_templates = len([f for f in files if f.file_type == FileType.TEMPLATE])
    total_data_files = len([f for f in files if f.file_type == FileType.DATA])
    total_size = sum(f.file_size for f in files)
    
    return FileStatistics(
        total_files=total_files,
        total_templates=total_templates,
        total_data_files=total_data_files,
        total_size=total_size
    )
