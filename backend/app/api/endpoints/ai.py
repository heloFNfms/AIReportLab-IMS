"""
AI 辅助功能 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import asyncio

from app.models.user import User
from app.core.deps import get_current_user
from app.services.ai_service import stream_ai_response, call_ai

router = APIRouter()


class AIRequest(BaseModel):
    """AI 请求模型"""
    text: str = Field(..., description="要处理的文本", max_length=6000)
    action: str = Field(..., description="操作类型: polish/expand/condense/rewrite/continue/explain/translate_en/translate_zh/custom")
    custom_prompt: Optional[str] = Field(None, description="自定义 prompt（当 action 为 custom 时使用）")


class AIResponse(BaseModel):
    """AI 响应模型"""
    success: bool
    result: str
    action: str


@router.post("/process", response_model=AIResponse)
async def process_text(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):
    """
    处理文本（非流式）
    适用于短文本的快速处理
    """
    try:
        result = await call_ai(request.text, request.action, request.custom_prompt)
        return AIResponse(success=True, result=result, action=request.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 处理失败: {str(e)}")


@router.post("/stream")
async def stream_process_text(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):
    """
    流式处理文本
    返回 Server-Sent Events (SSE) 格式的流式响应
    """
    async def generate():
        try:
            async for chunk in stream_ai_response(request.text, request.action, request.custom_prompt):
                # SSE 格式
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except ValueError as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        except Exception as e:
            yield f"data: [ERROR] AI 处理失败: {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/actions")
async def get_available_actions(
    current_user: User = Depends(get_current_user)
):
    """获取可用的 AI 操作列表"""
    return {
        "actions": [
            {"id": "polish", "name": "润色", "description": "优化语言表达，使文本更专业流畅", "icon": "✨"},
            {"id": "expand", "name": "扩写", "description": "扩展内容，增加更多细节", "icon": "📝"},
            {"id": "condense", "name": "缩写", "description": "精简内容，保留核心要点", "icon": "📉"},
            {"id": "rewrite", "name": "改写", "description": "换一种表达方式", "icon": "🔄"},
            {"id": "continue", "name": "续写", "description": "根据上下文续写内容", "icon": "➡️"},
            {"id": "explain", "name": "解释", "description": "解释专业术语或概念", "icon": "💡"},
            {"id": "translate_en", "name": "翻译英文", "description": "翻译成英文", "icon": "🇬🇧"},
            {"id": "translate_zh", "name": "翻译中文", "description": "翻译成中文", "icon": "🇨🇳"},
        ]
    }
