"""
AI服务模块
提供AI相关的服务，包括模板分析、报告生成等功能
"""

from app.services.ai.base import AIClientBase
from app.services.ai.template_analyzer import TemplateAnalyzer
from app.services.ai.report_generator import ReportGenerator

__all__ = [
    'AIClientBase',
    'TemplateAnalyzer',
    'ReportGenerator',
]
