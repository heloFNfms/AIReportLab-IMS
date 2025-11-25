"""
测试 DeepSeek API 连接
验证配置是否正确
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai.base import get_ai_client
from app.core.config import settings


async def test_deepseek_connection():
    """测试DeepSeek API连接"""
    
    print("=" * 50)
    print("🧪 DeepSeek API 连接测试")
    print("=" * 50)
    
    # 显示当前配置
    print("\n📋 当前配置：")
    print(f"  提供商: {settings.AI_PROVIDER}")
    print(f"  API Key: {settings.AI_API_KEY[:15]}...")
    print(f"  Base URL: {settings.AI_BASE_URL}")
    print(f"  模型: {settings.AI_MODEL}")
    
    # 获取AI客户端
    print("\n🔌 正在连接 DeepSeek...")
    client = get_ai_client()
    
    try:
        # 测试1: 简单对话
        print("\n✅ 测试1: 简单对话")
        messages = [
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ]
        
        response = await client.chat_completion(messages=messages, temperature=0.7)
        print(f"  响应: {response}")
        
        # 测试2: 结构化输出
        print("\n✅ 测试2: 结构化输出 (JSON)")
        prompt = """
        请分析以下报告模板片段，输出JSON格式：
        
        模板内容：
        一、项目概述
        本章节介绍项目的背景和目标。
        
        二、技术方案
        详细说明技术实现方案。
        """
        
        schema = {
            "章节结构": [
                {"章节名": "string", "内容要求": "string"}
            ]
        }
        
        result = await client.structured_output(prompt=prompt, schema=schema)
        print(f"  结果: {result}")
        
        print("\n" + "=" * 50)
        print("✅ DeepSeek API 测试通过！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ 测试失败: {str(e)}")
        print("=" * 50)
        print("\n💡 可能的问题：")
        print("  1. API Key 不正确")
        print("  2. 网络连接问题")
        print("  3. API 服务暂时不可用")
        return False


if __name__ == '__main__':
    success = asyncio.run(test_deepseek_connection())
    sys.exit(0 if success else 1)
