"""
草稿/报告管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.models.user import User
from app.models.draft import Draft, DraftVersion
from app.models.file import File
from app.schemas.draft import (
    DraftCreate, DraftUpdate, DraftComplete,
    DraftResponse, DraftListResponse, DraftVersionResponse,
    DraftWithVersionsResponse
)
from app.core.deps import get_current_user

router = APIRouter()


def count_words(text: str) -> int:
    """统计字数"""
    if not text:
        return 0
    # 简单统计：中文字符 + 英文单词
    import re
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(
    draft_data: DraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新草稿"""
    # 如果指定了模板文件，验证文件存在且属于当前用户
    if draft_data.template_file_id:
        template_file = db.query(File).filter(
            File.id == draft_data.template_file_id,
            File.user_id == current_user.id
        ).first()
        if not template_file:
            raise HTTPException(status_code=404, detail="模板文件不存在")
    
    word_count = count_words(draft_data.content) if draft_data.content else 0
    
    db_draft = Draft(
        title=draft_data.title,
        user_id=current_user.id,
        template_file_id=draft_data.template_file_id,
        data_file_id=draft_data.data_file_id,
        content=draft_data.content or "",
        status="draft",
        current_version=1,
        word_count=word_count
    )
    
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    
    # 创建初始版本
    initial_version = DraftVersion(
        draft_id=db_draft.id,
        version=1,
        content=draft_data.content or "",
        word_count=word_count,
        change_summary="初始创建"
    )
    db.add(initial_version)
    db.commit()
    
    return db_draft


@router.get("/", response_model=List[DraftListResponse])
def get_drafts(
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有草稿/报告"""
    query = db.query(Draft).filter(Draft.user_id == current_user.id)
    if status_filter:
        query = query.filter(Draft.status == status_filter)
    return query.order_by(Draft.updated_at.desc()).all()


# 注意：statistics 路由必须在 /{draft_id} 之前定义，否则会被当作 draft_id 匹配
@router.get("/statistics")
def get_draft_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取草稿统计"""
    drafts = db.query(Draft).filter(Draft.user_id == current_user.id).all()
    return {
        "total": len(drafts),
        "draft_count": len([d for d in drafts if d.status == "draft"]),
        "completed_count": len([d for d in drafts if d.status == "completed"])
    }


@router.get("/{draft_id}", response_model=DraftWithVersionsResponse)
def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个草稿详情（包含版本历史）"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    return draft


@router.put("/{draft_id}", response_model=DraftResponse)
def update_draft(
    draft_id: int,
    draft_data: DraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新草稿（自动保存新版本）"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 更新字段
    if draft_data.title is not None:
        draft.title = draft_data.title
    if draft_data.data_file_id is not None:
        draft.data_file_id = draft_data.data_file_id
    
    # 如果内容有变化，创建新版本
    if draft_data.content is not None and draft_data.content != draft.content:
        draft.current_version += 1
        draft.content = draft_data.content
        draft.word_count = count_words(draft_data.content)
        
        # 保存新版本
        new_version = DraftVersion(
            draft_id=draft.id,
            version=draft.current_version,
            content=draft_data.content,
            word_count=draft.word_count,
            change_summary=draft_data.change_summary or f"版本 {draft.current_version}"
        )
        db.add(new_version)
    
    db.commit()
    db.refresh(draft)
    return draft


@router.post("/{draft_id}/complete", response_model=DraftResponse)
def complete_draft(
    draft_id: int,
    complete_data: DraftComplete = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成草稿，标记为已完成"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 更新最终内容
    if complete_data:
        if complete_data.title:
            draft.title = complete_data.title
        if complete_data.content:
            draft.content = complete_data.content
            draft.word_count = count_words(complete_data.content)
    
    draft.status = "completed"
    draft.completed_at = datetime.now()
    
    # 保存最终版本
    draft.current_version += 1
    final_version = DraftVersion(
        draft_id=draft.id,
        version=draft.current_version,
        content=draft.content,
        word_count=draft.word_count,
        change_summary="完成报告"
    )
    db.add(final_version)
    
    db.commit()
    db.refresh(draft)
    return draft


@router.post("/{draft_id}/reopen", response_model=DraftResponse)
def reopen_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新打开已完成的报告进行编辑"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    draft.status = "draft"
    draft.completed_at = None
    
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{draft_id}/versions", response_model=List[DraftVersionResponse])
def get_draft_versions(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取草稿的所有版本"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    versions = db.query(DraftVersion).filter(
        DraftVersion.draft_id == draft_id
    ).order_by(DraftVersion.version.desc()).all()
    
    return versions


@router.post("/{draft_id}/rollback/{version}", response_model=DraftResponse)
def rollback_draft(
    draft_id: int,
    version: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """回滚到指定版本"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 获取目标版本
    target_version = db.query(DraftVersion).filter(
        DraftVersion.draft_id == draft_id,
        DraftVersion.version == version
    ).first()
    
    if not target_version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 创建新版本（回滚记录）
    draft.current_version += 1
    draft.content = target_version.content
    draft.word_count = target_version.word_count
    
    rollback_version = DraftVersion(
        draft_id=draft.id,
        version=draft.current_version,
        content=target_version.content,
        word_count=target_version.word_count,
        change_summary=f"回滚到版本 {version}"
    )
    db.add(rollback_version)
    
    db.commit()
    db.refresh(draft)
    return draft


@router.delete("/{draft_id}")
def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除草稿"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    db.delete(draft)
    db.commit()
    return {"message": "草稿删除成功"}
