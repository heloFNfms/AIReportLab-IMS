from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response
from fastapi.responses import FileResponse as FastAPIFileResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import io
import csv
import json
import mimetypes
import httpx
from app.db.database import get_db
from app.models.user import User
from app.models.file import FileType, File as FileModel
from app.schemas.file import FileResponse, FileStatistics, FilePreviewResponse
from app.services.file_service import save_upload_file, get_user_files, get_file_by_id, delete_file, get_file_statistics
from app.services.oss_service import oss_service
from app.core.deps import get_current_user
from app.services.ai.template_analyzer import template_analyzer

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

@router.get("/{file_id}/preview", response_model=FilePreviewResponse)
async def preview_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """预览文件内容，支持 JSON/CSV/TXT/DOCX（文本提取）"""
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问"
        )

    mime = file.mime_type or mimetypes.guess_type(file.file_path)[0] or "application/octet-stream"

    async def _process_bytes(data: bytes):
        if mime.startswith("application/json") or file.filename.lower().endswith(".json"):
            try:
                obj = json.loads(data.decode("utf-8"))
                return FilePreviewResponse(mime_type=mime, preview_type="json", content=obj)
            except Exception:
                # 回退为文本
                text = data.decode("utf-8", errors="ignore")
                return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)
        if mime in ("text/csv", "application/csv") or file.filename.lower().endswith(".csv"):
            try:
                text = data.decode("utf-8", errors="ignore")
                reader = csv.reader(io.StringIO(text))
                rows = []
                for idx, row in enumerate(reader):
                    rows.append(row)
                    if idx >= 199:
                        break
                return FilePreviewResponse(mime_type=mime, preview_type="csv", csv_rows=rows)
            except Exception:
                text = data.decode("utf-8", errors="ignore")
                return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)
        if mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",) or file.filename.lower().endswith(".docx"):
            try:
                import docx
                doc = docx.Document(io.BytesIO(data))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return FilePreviewResponse(mime_type=mime, preview_type="text", content="\n".join(paragraphs))
            except Exception:
                text = data.decode("utf-8", errors="ignore")
                return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)
        # 默认视为文本
        text = data.decode("utf-8", errors="ignore")
        return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)

    # OSS 文件：通过签名URL获取内容
    if file.is_oss and file.oss_path:
        try:
            signed_url = oss_service.get_file_url(file.oss_path)
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(signed_url)
                if resp.status_code != 200:
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OSS文件预览获取失败")
                return await _process_bytes(resp.content)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"预览失败: {str(e)}")

    # 本地文件
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    try:
        if mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",) or file.filename.lower().endswith(".docx"):
            text = template_analyzer.extract_text_from_docx(file.file_path)
            return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)
        if mime in ("text/plain",) or file.filename.lower().endswith(".txt"):
            text = template_analyzer.extract_text_from_txt(file.file_path)
            return FilePreviewResponse(mime_type=mime, preview_type="text", content=text)
        # 其他类型按二进制读取并走通用处理
        with open(file.file_path, "rb") as f:
            data = f.read()
            return await _process_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"预览失败: {str(e)}")
