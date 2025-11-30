"""
报告生成API端点
提供报告的生成、查询和管理功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.report import Report, ReportStatus
from app.models.template import Template, TemplateStatus
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportGenerateRequest,
    ReportResponse,
    ReportListResponse,
    ReportStatusResponse,
    DraftSaveRequest,
    DraftResponse
)
from app.core.deps import get_current_user
from app.services.ai.report_generator import report_generator
from app.db.database import SessionLocal
from app.models.file import File as FileModel
from app.services.oss_service import oss_service
import json
import asyncio
import httpx
import os
from datetime import datetime
from app.core.config import settings

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成报告（异步任务）
    
    - **template_id**: 使用的模板ID
    - **data_file_id**: 数据文件ID（可选）
    - **custom_data**: 自定义数据（可选）
    - **title**: 报告标题（可选）
    - **requirements**: 额外要求（可选）
    - **ai_model**: 指定AI模型（可选）
    - **temperature**: 生成温度（可选，默认0.7）
    """
    # 验证模板是否存在
    template = db.query(Template).filter(
        Template.id == request.template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )
    
    # 检查模板是否已分析
    if template.status != TemplateStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="模板尚未分析完成，请先分析模板"
        )
    
    # 创建报告记录
    db_report = Report(
        title=request.title or f"{template.name} - 自动生成报告",
        template_id=request.template_id,
        data_file_id=request.data_file_id,
        user_id=current_user.id,
        status=ReportStatus.PENDING,
        progress=0,
        generation_params={
            "ai_model": request.ai_model,
            "temperature": request.temperature,
            "custom_requirements": request.requirements
        }
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # 启动后台任务：分段生成报告
    # 为提高可靠性，使用 BackgroundTasks 触发
    background_tasks.add_task(asyncio.create_task, generate_report_task(db_report.id))
    
    return db_report


@router.get("/", response_model=List[ReportListResponse])
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有报告"""
    reports = db.query(Report).filter(
        Report.user_id == current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个报告详情"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    return report


@router.get("/{report_id}/status", response_model=ReportStatusResponse)
def get_report_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取报告生成状态"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    return {
        "status": report.status,
        "progress": report.progress,
        "error_message": report.error_message,
        "completed_at": report.completed_at
    }


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新报告"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    # 更新字段
    update_data = report_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除报告"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "报告删除成功"}


@router.post("/drafts", response_model=DraftResponse)
def save_draft(
    draft: DraftSaveRequest,
    current_user: User = Depends(get_current_user)
):
    """保存草稿到本地 uploads/drafts/{user_id}/{template_id}.md"""
    base_dir = os.path.join(settings.UPLOAD_FOLDER, "drafts", str(current_user.id))
    os.makedirs(base_dir, exist_ok=True)
    file_path = os.path.join(base_dir, f"{draft.template_id}.md")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(draft.content)
        return DraftResponse(
            template_id=draft.template_id,
            title=draft.title,
            content=draft.content,
            format=draft.format,
            updated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"保存草稿失败: {str(e)}")


@router.get("/drafts/{template_id}", response_model=DraftResponse)
def get_draft(
    template_id: int,
    current_user: User = Depends(get_current_user)
):
    """读取草稿，如果不存在返回404"""
    base_dir = os.path.join(settings.UPLOAD_FOLDER, "drafts", str(current_user.id))
    file_path = os.path.join(base_dir, f"{template_id}.md")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="草稿不存在")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return DraftResponse(
            template_id=template_id,
            title=None,
            content=content,
            format="markdown",
            updated_at=datetime.fromtimestamp(os.path.getmtime(file_path))
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"读取草稿失败: {str(e)}")


async def generate_report_task(report_id: int):
    """后台任务：根据模板结构分段生成报告并更新进度"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return
        template = db.query(Template).filter(Template.id == report.template_id).first()
        if not template or not template.structure:
            report.status = ReportStatus.FAILED
            report.error_message = "模板结构不存在"
            db.commit()
            return

        report.status = ReportStatus.GENERATING
        report.progress = 0
        db.commit()

        # 准备数据
        data_dict = {}
        data_req = []
        try:
            data_req = (template.structure or {}).get("数据要求", []) or []
        except Exception:
            data_req = []

        if report.data_file_id:
            file = db.query(FileModel).filter(FileModel.id == report.data_file_id).first()
            file_text = ""
            if file:
                try:
                    if file.is_oss and file.oss_path:
                        # 使用签名URL直接读取内容
                        signed_url = oss_service.get_file_url(file.oss_path)
                        async with httpx.AsyncClient() as client:
                            resp = await client.get(signed_url)
                            resp.raise_for_status()
                            file_text = resp.text
                    else:
                        if file.file_path and os.path.exists(file.file_path):
                            # 优先尝试 JSON
                            if file.file_path.lower().endswith(".json"):
                                with open(file.file_path, "r", encoding="utf-8") as f:
                                    data_dict = json.load(f)
                            else:
                                with open(file.file_path, "r", encoding="utf-8", errors="ignore") as f:
                                    file_text = f.read()
                except Exception:
                    file_text = ""

            # 若非JSON，尝试结构化抽取
            if not data_dict and file_text:
                try:
                    data_dict = await report_generator.extract_data_from_file(file_text, data_req)
                except Exception:
                    data_dict = {}

        # 分段生成
        sections = (template.structure or {}).get("章节结构", []) or []
        total = max(len(sections), 1)
        content_map = {}
        context = ""

        for idx, section in enumerate(sections, start=1):
            try:
                text = await report_generator.generate_section(
                    section_info=section,
                    template_structure=template.structure,
                    data=data_dict,
                    context=context,
                )
                name = section.get("章节名", f"章节{idx}")
                content_map[name] = text
                context += f"\n\n{name}:\n{text[:500]}..."
            except Exception as e:
                report.status = ReportStatus.FAILED
                report.error_message = f"章节生成失败: {str(e)}"
                db.commit()
                return

            # 更新进度
            report.progress = int(idx * 100 / total)
            db.commit()

        # 拼接全文
        full_text_parts = []
        for name, text in content_map.items():
            full_text_parts.append(f"# {name}\n\n{text}\n")
        report.content = content_map
        report.full_text = "\n".join(full_text_parts)
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.now()
        db.commit()
    finally:
        db.close()
