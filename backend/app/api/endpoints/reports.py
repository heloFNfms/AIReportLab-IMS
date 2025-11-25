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
    ReportStatusResponse
)
from app.core.deps import get_current_user
from app.services.ai.report_generator import report_generator
from datetime import datetime

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
    
    # TODO: 添加后台任务进行报告生成
    # background_tasks.add_task(
    #     generate_report_task,
    #     report_id=db_report.id,
    #     template_structure=template.structure,
    #     custom_data=request.custom_data
    # )
    
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


# TODO: 后台任务函数（在实际实现时启用）
# async def generate_report_task(
#     report_id: int,
#     template_structure: dict,
#     custom_data: dict = None
# ):
#     """后台任务：生成报告内容"""
#     pass
