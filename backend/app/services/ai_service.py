"""
AI 服务 - DeepSeek API 集成
支持流式输出的文本处理功能
"""
import os
import json
import httpx
from typing import AsyncGenerator, Optional

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    DEEPSEEK_API_KEY = "sk-c1991f56e6684c288ce54ee5034f4c04"
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"


# AI 操作类型对应的 prompt 模板
PROMPTS = {
    "polish": """请润色以下文本，使其更加专业、流畅、易读。保持原意不变，只优化语言表达。
直接输出润色后的文本，不要添加任何解释或前缀。

原文：
{text}""",

    "expand": """请扩写以下文本，增加更多细节和内容，使其更加丰富完整。保持原有风格和主题。
直接输出扩写后的文本，不要添加任何解释或前缀。

原文：
{text}""",

    "condense": """请精简以下文本，保留核心内容，去除冗余表达，使其更加简洁有力。
直接输出精简后的文本，不要添加任何解释或前缀。

原文：
{text}""",

    "rewrite": """请用不同的表达方式改写以下文本，保持原意但换一种说法。
直接输出改写后的文本，不要添加任何解释或前缀。

原文：
{text}""",

    "continue": """请根据以下文本的上下文，续写后续内容。保持风格一致，内容连贯。
直接输出续写的内容，不要添加任何解释或前缀。

已有内容：
{text}""",

    "explain": """请解释以下文本中的专业术语或概念，用通俗易懂的语言说明。

文本：
{text}""",

    "translate_en": """请将以下文本翻译成英文，保持专业性和准确性。
直接输出翻译结果，不要添加任何解释。

原文：
{text}""",

    "translate_zh": """请将以下文本翻译成中文，保持专业性和准确性。
直接输出翻译结果，不要添加任何解释。

原文：
{text}""",

    "custom": """{prompt}

文本：
{text}""",

    "ask": """{prompt}""",

    "outline": """请根据以下信息生成一份详细的报告大纲。

报告主题：{topic}
报告类型：{report_type}
目标受众：{audience}
{additional_info}

要求：
1. 生成清晰的多级标题结构（使用 Markdown 格式）
2. 每个章节包含简要说明
3. 结构合理，逻辑清晰
4. 适合 {report_type} 类型的报告

请直接输出 Markdown 格式的大纲，不要添加任何解释。"""
}


async def stream_ai_response(
    text: str,
    action: str,
    custom_prompt: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    流式调用 DeepSeek API
    
    Args:
        text: 要处理的文本
        action: 操作类型 (polish/expand/condense/rewrite/continue/explain/custom)
        custom_prompt: 自定义 prompt（当 action 为 custom 时使用）
    
    Yields:
        AI 生成的文本片段
    """
    # 构建 prompt
    if action == "ask":
        # 问答模式：custom_prompt 是用户的问题，text 是可选的上下文
        if text and text.strip():
            prompt = f"""请根据以下参考内容回答用户的问题。

参考内容：
{text}

用户问题：
{custom_prompt}"""
        else:
            prompt = custom_prompt or ""
    elif action == "outline":
        # 大纲生成模式：custom_prompt 包含 JSON 格式的参数
        import json
        try:
            params = json.loads(custom_prompt) if custom_prompt else {}
            topic = params.get('topic', '')
            report_type = params.get('report_type', '通用报告')
            audience = params.get('audience', '一般读者')
            additional_requirements = params.get('additional_requirements', '')
            
            additional_info = f"其他要求：{additional_requirements}" if additional_requirements else ""
            
            prompt = PROMPTS["outline"].format(
                topic=topic,
                report_type=report_type,
                audience=audience,
                additional_info=additional_info
            )
        except:
            raise ValueError("大纲生成参数格式错误")
    elif action == "custom" and custom_prompt:
        prompt = PROMPTS["custom"].format(prompt=custom_prompt, text=text)
    elif action in PROMPTS:
        prompt = PROMPTS[action].format(text=text)
    else:
        raise ValueError(f"不支持的操作类型: {action}")
    
    # 限制输入长度（约 2000 字），问答模式可以没有文本
    if action != "ask" and len(text) > 6000:
        raise ValueError("文本过长，请选择较短的内容（建议 2000 字以内）")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的写作助手，帮助用户优化和改进文本内容。"},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{DEEPSEEK_API_BASE}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"API 调用失败: {response.status_code} - {error_text.decode()}")
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue


async def call_ai(
    text: str,
    action: str,
    custom_prompt: Optional[str] = None
) -> str:
    """
    非流式调用 DeepSeek API（用于简单场景）
    
    Returns:
        完整的 AI 响应文本
    """
    result = []
    async for chunk in stream_ai_response(text, action, custom_prompt):
        result.append(chunk)
    return "".join(result)
