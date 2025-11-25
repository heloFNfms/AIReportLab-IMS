"""
模板分析器
负责使用AI分析报告模板，提取结构化信息
"""

from typing import Dict, Any, Optional
from app.services.ai.base import get_ai_client
import docx
import json


class TemplateAnalyzer:
    """模板分析器：使用AI理解和分析报告模板"""
    
    def __init__(self):
        self.ai_client = get_ai_client()
    
    async def analyze_template(
        self,
        template_content: str,
        template_name: str = "未命名模板"
    ) -> Dict[str, Any]:
        """
        分析模板内容，提取结构化信息
        
        Args:
            template_content: 模板的文本内容
            template_name: 模板名称
            
        Returns:
            结构化的模板分析结果
        """
        # 定义期望的输出结构
        schema = {
            "报告名称": "string",
            "报告类型": "string",
            "章节结构": [
                {
                    "章节名": "string",
                    "章节级别": "number (1-3)",
                    "内容要求": "string",
                    "字数建议": "string (可选)"
                }
            ],
            "风格要求": "string",
            "格式规则": {
                "标题层级": ["string"],
                "引用格式": "string (可选)",
                "其他规则": "string (可选)"
            },
            "数据要求": ["string"],
            "特殊说明": "string (可选)"
        }
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(template_content, template_name)
        
        # 调用AI进行结构化分析
        result = await self.ai_client.structured_output(
            prompt=prompt,
            schema=schema
        )
        
        return result
    
    async def analyze_template_in_chunks(
        self,
        template_content: str,
        template_name: str = "未命名模板",
        chunk_size: int = 4000
    ) -> Dict[str, Any]:
        """
        分块分析长模板
        
        Args:
            template_content: 模板的文本内容
            template_name: 模板名称
            chunk_size: 每块的字符数
            
        Returns:
            合并后的结构化分析结果
        """
        # 如果内容较短，直接分析
        if len(template_content) <= chunk_size:
            return await self.analyze_template(template_content, template_name)
        
        # 分块处理
        chunks = self._split_into_chunks(template_content, chunk_size)
        partial_results = []
        
        for i, chunk in enumerate(chunks):
            prompt = self._build_chunk_analysis_prompt(chunk, i + 1, len(chunks))
            result = await self.ai_client.structured_output(
                prompt=prompt,
                schema={"章节结构": "array", "关键信息": "string"}
            )
            partial_results.append(result)
        
        # 合并结果
        final_result = await self._merge_partial_results(
            partial_results,
            template_name
        )
        
        return final_result
    
    def _build_analysis_prompt(self, content: str, name: str) -> str:
        """构建模板分析的提示词"""
        return f"""
你是一个专业的报告模板分析专家。
用户上传了一个名为"{name}"的报告模板，请你仔细阅读并分析其结构。

你的任务是：
1. 识别报告的类型和用途
2. 提取所有章节的名称、层级和内容要求
3. 总结报告的写作风格和语言特点
4. 归纳格式规则（标题、引用、排版等）
5. 分析报告需要的数据类型

模板内容：
{content[:8000]}

请严格按照指定的JSON格式输出分析结果。
"""
    
    def _build_chunk_analysis_prompt(self, chunk: str, index: int, total: int) -> str:
        """构建分块分析的提示词"""
        return f"""
这是一个长报告模板的第 {index}/{total} 部分。
请分析这部分内容中的章节结构和关键信息。

内容：
{chunk}

请输出这部分的章节结构和关键要点。
"""
    
    def _split_into_chunks(self, content: str, chunk_size: int) -> list:
        """将长文本分块"""
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunks.append(content[i:i + chunk_size])
        return chunks
    
    async def _merge_partial_results(
        self,
        partial_results: list,
        template_name: str
    ) -> Dict[str, Any]:
        """合并分块分析的结果"""
        merge_prompt = f"""
以下是对报告模板"{template_name}"的多个部分分析结果，
请将它们整合成一个完整的、结构化的模板分析报告。

分析结果：
{json.dumps(partial_results, ensure_ascii=False, indent=2)}

请输出完整的模板分析，包含所有章节、风格要求等信息。
"""
        
        schema = {
            "报告名称": "string",
            "报告类型": "string",
            "章节结构": "array",
            "风格要求": "string",
            "格式规则": "object"
        }
        
        result = await self.ai_client.structured_output(
            prompt=merge_prompt,
            schema=schema
        )
        
        return result
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从Word文档中提取文本"""
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """从文本文件中提取内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


# 创建单例
template_analyzer = TemplateAnalyzer()
