"""
AI客户端基类
提供统一的AI调用接口，支持多种AI模型（OpenAI、Claude等）
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.core.config import settings
import httpx


class AIClientBase(ABC):
    """AI客户端基类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化AI客户端
        
        Args:
            api_key: API密钥，如果不提供则从配置读取
            base_url: API基础URL，如果不提供则从配置读取
        """
        self.api_key = api_key or settings.AI_API_KEY
        self.base_url = base_url or settings.AI_BASE_URL
        self.model = settings.AI_MODEL
        self.timeout = settings.AI_TIMEOUT
        
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            AI的回复内容
        """
        pass
    
    @abstractmethod
    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        结构化输出接口
        
        Args:
            prompt: 提示词
            schema: 期望的输出结构（JSON Schema）
            **kwargs: 其他参数
            
        Returns:
            结构化的JSON数据
        """
        pass
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


class OpenAIClient(AIClientBase):
    """OpenAI客户端实现"""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """调用OpenAI聊天完成API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            payload.update(kwargs)
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用OpenAI的结构化输出功能
        提示AI返回符合特定JSON Schema的数据
        """
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的数据分析助手，请严格按照要求的JSON格式输出。"
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n请严格按照以下JSON Schema格式输出：\n{schema}"
            }
        ]
        
        response = await self.chat_completion(
            messages=messages,
            temperature=0.3,  # 降低温度以获得更稳定的结构化输出
            **kwargs
        )
        
        # 尝试解析JSON
        import json
        try:
            # 提取JSON内容（处理可能的markdown代码块）
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"AI返回的内容不是有效的JSON格式: {response}")


# 工厂函数：根据配置创建AI客户端
def get_ai_client() -> AIClientBase:
    """
    获取AI客户端实例
    根据配置选择对应的客户端实现
    """
    provider = settings.AI_PROVIDER.lower()
    
    if provider == "openai":
        return OpenAIClient()
    # 后续可以扩展其他提供商
    # elif provider == "claude":
    #     return ClaudeClient()
    # elif provider == "deepseek":
    #     return DeepSeekClient()
    else:
        # 默认使用OpenAI
        return OpenAIClient()
