"""
草稿管理API端点
提供草稿的创建、保存、版本历史和编辑阶段管理功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.draft import Draft, DraftVersion, EditingStage
from app.models.template import Template
from app.schemas.draft import (
    DraftSaveRequest,
    DraftResponse,
    DraftWithContentResponse,
    DraftVersionResponse,
    DraftVersionListResponse,
    EditingStageUpdateRequest
)
from app.core.deps import get_current_user
from datetime import datetime

router = APIRouter()


@router.post("/drafts", response_model=DraftWithContentResponse)
def save_draft(
    draft_req: DraftSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存草稿（创建新版本）
    
    - 如果草稿不存在，创建新草稿和第一个版本
    - 如果草稿已存在，创建新版本并更新current_version_id
    """
    # 验证模板是否存在且属于当前用户
    template = db.query(Template).filter(
        Template.id == draft_req.template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    # 查找或创建草稿
    draft = db.query(Draft).filter(
        Draft.template_id == draft_req.template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        # 创建新草稿
        draft = Draft(
            template_id=draft_req.template_id,
            user_id=current_user.id,
            title=draft_req.title or template.name,
            editing_stage=EditingStage.DRAFT
        )
        db.add(draft)
        db.flush()  # 获取draft.id
        version_number = 1
    else:
        # 更新草稿标题（如果提供）
        if draft_req.title:
            draft.title = draft_req.title
        # 计算新版本号
        max_version = db.query(DraftVersion).filter(
            DraftVersion.draft_id == draft.id
        ).count()
        version_number = max_version + 1
    
    # 创建新版本
    new_version = DraftVersion(
        draft_id=draft.id,
        version_number=version_number,
        content=draft_req.content,
        format=draft_req.format,
        change_summary=draft_req.change_summary,
        word_count=len(draft_req.content),
        created_by=current_user.id
    )
    db.add(new_version)
    db.flush()
    
    # 更新草稿的当前版本
    draft.current_version_id = new_version.id
    db.commit()
    db.refresh(draft)
    db.refresh(new_version)
    
    return DraftWithContentResponse(
        id=draft.id,
        template_id=draft.template_id,
        user_id=draft.user_id,
        title=draft.title,
        editing_stage=draft.editing_stage.value,
        current_version=DraftVersionResponse(
            id=new_version.id,
            draft_id=new_version.draft_id,
            version_number=new_version.version_number,
            content=new_version.content,
            format=new_version.format,
            change_summary=new_version.change_summary,
            word_count=new_version.word_count,
            created_at=new_version.created_at,
            created_by=new_version.created_by
        ),
        created_at=draft.created_at,
        updated_at=draft.updated_at
    )


@router.get("/drafts/{template_id}", response_model=DraftWithContentResponse)
def get_draft(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取草稿及其当前版本内容"""
    draft = db.query(Draft).filter(
        Draft.template_id == template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    # 获取当前版本
    current_version = None
    if draft.current_version_id:
        version = db.query(DraftVersion).filter(
            DraftVersion.id == draft.current_version_id
        ).first()
        if version:
            current_version = DraftVersionResponse(
                id=version.id,
                draft_id=version.draft_id,
                version_number=version.version_number,
                content=version.content,
                format=version.format,
                change_summary=version.change_summary,
                word_count=version.word_count,
                created_at=version.created_at,
                created_by=version.created_by
            )
    
    return DraftWithContentResponse(
        id=draft.id,
        template_id=draft.template_id,
        user_id=draft.user_id,
        title=draft.title,
        editing_stage=draft.editing_stage.value,
        current_version=current_version,
        created_at=draft.created_at,
        updated_at=draft.updated_at
    )


@router.get("/drafts/{template_id}/versions", response_model=DraftVersionListResponse)
def get_draft_versions(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取草稿的所有版本历史"""
    draft = db.query(Draft).filter(
        Draft.template_id == template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    versions = db.query(DraftVersion).filter(
        DraftVersion.draft_id == draft.id
    ).order_by(DraftVersion.version_number.desc()).all()
    
    return DraftVersionListResponse(
        versions=[
            DraftVersionResponse(
                id=v.id,
                draft_id=v.draft_id,
                version_number=v.version_number,
                content=v.content,
                format=v.format,
                change_summary=v.change_summary,
                word_count=v.word_count,
                created_at=v.created_at,
                created_by=v.created_by
            ) for v in versions
        ],
        total=len(versions)
    )


@router.get("/drafts/{template_id}/versions/{version_id}", response_model=DraftVersionResponse)
def get_draft_version(
    template_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定版本的内容"""
    draft = db.query(Draft).filter(
        Draft.template_id == template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    version = db.query(DraftVersion).filter(
        DraftVersion.id == version_id,
        DraftVersion.draft_id == draft.id
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    return DraftVersionResponse(
        id=version.id,
        draft_id=version.draft_id,
        version_number=version.version_number,
        content=version.content,
        format=version.format,
        change_summary=version.change_summary,
        word_count=version.word_count,
        created_at=version.created_at,
        created_by=version.created_by
    )


@router.post("/drafts/{template_id}/restore/{version_id}", response_model=DraftWithContentResponse)
def restore_draft_version(
    template_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """恢复到指定版本（创建新版本，内容为指定版本的内容）"""
    draft = db.query(Draft).filter(
        Draft.template_id == template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    # 获取要恢复的版本
    restore_version = db.query(DraftVersion).filter(
        DraftVersion.id == version_id,
        DraftVersion.draft_id == draft.id
    ).first()
    
    if not restore_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 计算新版本号
    max_version = db.query(DraftVersion).filter(
        DraftVersion.draft_id == draft.id
    ).count()
    new_version_number = max_version + 1
    
    # 创建新版本（内容为恢复版本的内容）
    new_version = DraftVersion(
        draft_id=draft.id,
        version_number=new_version_number,
        content=restore_version.content,
        format=restore_version.format,
        change_summary=f"恢复到版本 {restore_version.version_number}",
        word_count=restore_version.word_count,
        created_by=current_user.id
    )
    db.add(new_version)
    db.flush()
    
    # 更新当前版本
    draft.current_version_id = new_version.id
    db.commit()
    db.refresh(draft)
    db.refresh(new_version)
    
    return DraftWithContentResponse(
        id=draft.id,
        template_id=draft.template_id,
        user_id=draft.user_id,
        title=draft.title,
        editing_stage=draft.editing_stage.value,
        current_version=DraftVersionResponse(
            id=new_version.id,
            draft_id=new_version.draft_id,
            version_number=new_version.version_number,
            content=new_version.content,
            format=new_version.format,
            change_summary=new_version.change_summary,
            word_count=new_version.word_count,
            created_at=new_version.created_at,
            created_by=new_version.created_by
        ),
        created_at=draft.created_at,
        updated_at=draft.updated_at
    )


@router.put("/drafts/{template_id}/stage", response_model=DraftResponse)
def update_editing_stage(
    template_id: int,
    stage_req: EditingStageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新草稿的编辑阶段"""
    draft = db.query(Draft).filter(
        Draft.template_id == template_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    # 验证编辑阶段值
    try:
        new_stage = EditingStage(stage_req.editing_stage)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的编辑阶段: {stage_req.editing_stage}。有效值: draft, reviewing, completed"
        )
    
    draft.editing_stage = new_stage
    db.commit()
    db.refresh(draft)
    
    return DraftResponse(
        id=draft.id,
        template_id=draft.template_id,
        user_id=draft.user_id,
        title=draft.title,
        current_version_id=draft.current_version_id,
        editing_stage=draft.editing_stage.value,
        created_at=draft.created_at,
        updated_at=draft.updated_at
    )
