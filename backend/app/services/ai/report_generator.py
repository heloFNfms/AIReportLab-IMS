"""
报告生成器
负责使用AI根据模板和数据生成报告内容
"""

from typing import Dict, Any, List, Optional
from app.services.ai.base import get_ai_client
import json


class ReportGenerator:
    """报告生成器：基于模板和数据生成报告"""
    
    def __init__(self):
        self.ai_client = get_ai_client()
    
    async def generate_section(
        self,
        section_info: Dict[str, Any],
        template_structure: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> str:
        """
        生成单个章节内容
        
        Args:
            section_info: 章节信息（名称、要求等）
            template_structure: 完整模板结构
            data: 相关数据
            context: 上下文信息
            
        Returns:
            生成的章节内容
        """
        prompt = self._build_section_prompt(
            section_info,
            template_structure,
            data,
            context
        )
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的报告写作助手，擅长根据模板要求撰写高质量的报告内容。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        content = await self.ai_client.chat_completion(
            messages=messages,
            temperature=0.7
        )
        
        return content
    
    async def generate_full_report(
        self,
        template_structure: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        生成完整报告
        
        Args:
            template_structure: 模板结构（来自TemplateAnalyzer）
            data: 报告所需数据
            
        Returns:
            各章节内容的字典
        """
        sections = template_structure.get("章节结构", [])
        report_sections = {}
        context = ""
        
        for section in sections:
            section_name = section.get("章节名", "")
            
            # 生成章节内容
            content = await self.generate_section(
                section_info=section,
                template_structure=template_structure,
                data=data,
                context=context
            )
            
            report_sections[section_name] = content
            
            # 累积上下文，供后续章节参考
            context += f"\n\n{section_name}:\n{content[:500]}..."
        
        return report_sections
    
    async def refine_content(
        self,
        content: str,
        requirements: str,
        max_iterations: int = 2
    ) -> str:
        """
        优化和润色内容
        
        Args:
            content: 原始内容
            requirements: 优化要求
            max_iterations: 最大迭代次数
            
        Returns:
            优化后的内容
        """
        refined = content
        
        for i in range(max_iterations):
            prompt = f"""
请根据以下要求优化这段内容：

要求：
{requirements}

原始内容：
{refined}

请输出优化后的内容，保持专业性和可读性。
"""
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            refined = await self.ai_client.chat_completion(
                messages=messages,
                temperature=0.5
            )
        
        return refined
    
    def _build_section_prompt(
        self,
        section_info: Dict[str, Any],
        template_structure: Dict[str, Any],
        data: Optional[Dict[str, Any]],
        context: Optional[str]
    ) -> str:
        """构建章节生成的提示词"""
        section_name = section_info.get("章节名", "")
        requirements = section_info.get("内容要求", "")
        word_count = section_info.get("字数建议", "")
        
        report_type = template_structure.get("报告类型", "")
        style = template_structure.get("风格要求", "")
        
        prompt = f"""
你正在撰写一份"{report_type}"报告的"{section_name}"章节。

章节要求：
{requirements}

写作风格：
{style}
"""
        
        if word_count:
            prompt += f"\n字数建议：{word_count}\n"
        
        if data:
            prompt += f"\n相关数据：\n{json.dumps(data, ensure_ascii=False, indent=2)}\n"
        
        if context:
            prompt += f"\n已完成的内容（供参考）：\n{context}\n"
        
        prompt += "\n请撰写这个章节的内容，确保逻辑清晰、数据准确、表达专业。"
        
        return prompt
    
    async def extract_data_from_file(
        self,
        file_content: str,
        data_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        从数据文件中提取所需信息
        
        Args:
            file_content: 数据文件内容
            data_requirements: 所需数据列表
            
        Returns:
            提取的数据
        """
        prompt = f"""
请从以下数据中提取所需的信息：

所需数据类型：
{json.dumps(data_requirements, ensure_ascii=False)}

数据内容：
{file_content[:5000]}

请以JSON格式输出提取的数据。
"""
        
        schema = {
            "extracted_data": "object"
        }
        
        result = await self.ai_client.structured_output(
            prompt=prompt,
            schema=schema
        )
        
        return result.get("extracted_data", {})


# 创建单例
report_generator = ReportGenerator()
