"""
模板管理API端点
提供模板的CRUD和AI分析功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.template import Template, TemplateStatus
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateAnalyzeRequest,
    TemplateResponse,
    TemplateListResponse
)
from app.core.deps import get_current_user
from app.services.ai.template_analyzer import template_analyzer
from datetime import datetime
from app.services.file_service import get_file_by_id
from app.models.file import File as FileModel
from app.services.oss_service import oss_service
import httpx

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新模板
    
    - **name**: 模板名称
    - **description**: 模板描述（可选）
    - **file_id**: 关联的文件ID（可选）
    - **content**: 模板内容文本（可选）
    """
    # TODO: 如果提供了file_id，从文件中提取内容
    # TODO: 实现文件内容提取逻辑
    
    db_template = Template(
        name=template_data.name,
        description=template_data.description,
        file_id=template_data.file_id,
        content=template_data.content,
        user_id=current_user.id,
        status=TemplateStatus.PENDING
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.get("/", response_model=List[TemplateListResponse])
def get_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有模板"""
    templates = db.query(Template).filter(
        Template.user_id == current_user.id
    ).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个模板详情"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新模板"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    # 更新字段
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除模板"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "模板删除成功"}


@router.post("/{template_id}/analyze", response_model=TemplateResponse)
async def analyze_template(
    template_id: int,
    force_reanalyze: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用AI分析模板结构
    
    - **template_id**: 模板ID
    - **force_reanalyze**: 是否强制重新分析（即使已有分析结果）
    """
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    # 检查是否需要分析
    if template.status == TemplateStatus.COMPLETED and not force_reanalyze:
        return template
    
    # 若无内容但有文件ID，则尝试从文件读取
    if not template.content:
        if template.file_id:
            file = db.query(FileModel).filter(
                FileModel.id == template.file_id,
                FileModel.user_id == current_user.id
            ).first()
            if not file:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联文件不存在或无权访问")

            try:
                if file.is_oss and file.oss_path:
                    # 直接获取签名URL并拉取内容
                    signed_url = oss_service.get_file_url(file.oss_path)
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(signed_url)
                        resp.raise_for_status()
                        template.content = resp.text
                else:
                    # 读取本地文件内容
                    path = file.file_path
                    # 简单按扩展名处理 txt/docx
                    if path and path.lower().endswith(".txt"):
                        with open(path, "r", encoding="utf-8") as f:
                            template.content = f.read()
                    elif path and path.lower().endswith(".docx"):
                        # 使用 analyzer 的 docx 提取辅助
                        template.content = template_analyzer.extract_text_from_docx(path)
                    else:
                        # 其他类型按文本尝试读取
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            template.content = f.read()
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"读取模板文件失败: {str(e)}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板内容为空，无法分析"
            )
    
    # 更新状态为分析中
    template.status = TemplateStatus.ANALYZING
    db.commit()
    
    try:
        analysis_result = await template_analyzer.analyze_template(
            template_content=template.content,
            template_name=template.name
        )
        
        # 保存分析结果
        template.structure = analysis_result
        template.status = TemplateStatus.COMPLETED
        template.analyzed_at = datetime.now()
        template.error_message = None
        
    except Exception as e:
        # 分析失败
        template.status = TemplateStatus.FAILED
        template.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模板分析失败: {str(e)}"
        )
    
    db.commit()
    db.refresh(template)
    
    return template
