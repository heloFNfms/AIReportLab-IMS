# AI服务框架说明文档

## 📋 概述

本框架为AIReportLab IMS项目提供完整的AI能力支撑，采用模块化设计，支持多种AI提供商，便于扩展和维护。

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   API 层                             │
│  /api/templates  |  /api/reports                    │
└───────────────┬─────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────┐
│                 服务层                               │
│  TemplateAnalyzer  |  ReportGenerator               │
└───────────────┬─────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────┐
│              AI 客户端层                             │
│  AIClientBase (抽象)                                 │
│    ↓                                                 │
│  OpenAIClient  |  ClaudeClient  |  DeepSeekClient   │
└─────────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────┐
│              外部 AI 服务                            │
│  OpenAI API  |  Claude API  |  DeepSeek API         │
└─────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
backend/
├── app/
│   ├── services/
│   │   └── ai/                      # AI服务模块
│   │       ├── __init__.py          # 模块导出
│   │       ├── base.py              # AI客户端基类
│   │       ├── template_analyzer.py # 模板分析器
│   │       └── report_generator.py  # 报告生成器
│   ├── models/
│   │   ├── template.py              # 模板数据模型
│   │   └── report.py                # 报告数据模型
│   ├── schemas/
│   │   ├── template.py              # 模板Schema
│   │   └── report.py                # 报告Schema
│   └── api/
│       └── endpoints/
│           ├── templates.py         # 模板API
│           └── reports.py           # 报告API
└── requirements.txt                 # 依赖包
```

## 🔧 核心组件

### 1. AI客户端基类 (AIClientBase)

**位置**: `app/services/ai/base.py`

**职责**:
- 提供统一的AI调用接口
- 支持多种AI提供商（OpenAI, Claude等）
- 处理API认证和请求

**核心方法**:
```python
async def chat_completion(messages, temperature, max_tokens)
    # 聊天完成接口

async def structured_output(prompt, schema)
    # 结构化输出接口（返回JSON）
```

**扩展新提供商**:
```python
class CustomAIClient(AIClientBase):
    async def chat_completion(self, messages, **kwargs):
        # 实现你的AI提供商调用逻辑
        pass
    
    async def structured_output(self, prompt, schema, **kwargs):
        # 实现结构化输出
        pass
```

### 2. 模板分析器 (TemplateAnalyzer)

**位置**: `app/services/ai/template_analyzer.py`

**职责**:
- 读取并解析报告模板
- 使用AI提取模板结构
- 支持多种格式（Word, Markdown, 文本）

**核心方法**:
```python
async def analyze_template(template_content, template_name)
    # 分析单个模板，返回结构化JSON

async def analyze_template_in_chunks(template_content, chunk_size)
    # 分块分析长模板
```

**输出结构**:
```json
{
  "报告名称": "string",
  "报告类型": "string",
  "章节结构": [
    {
      "章节名": "string",
      "章节级别": 1,
      "内容要求": "string",
      "字数建议": "string"
    }
  ],
  "风格要求": "string",
  "格式规则": {...},
  "数据要求": [...]
}
```

### 3. 报告生成器 (ReportGenerator)

**位置**: `app/services/ai/report_generator.py`

**职责**:
- 根据模板结构生成报告内容
- 支持分章节生成
- 内容优化和润色

**核心方法**:
```python
async def generate_section(section_info, template_structure, data, context)
    # 生成单个章节

async def generate_full_report(template_structure, data)
    # 生成完整报告

async def refine_content(content, requirements)
    # 优化内容
```

## 🔌 API端点

### 模板管理 API

**基础路径**: `/api/templates`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 创建模板 |
| GET | `/` | 获取模板列表 |
| GET | `/{id}` | 获取单个模板 |
| PUT | `/{id}` | 更新模板 |
| DELETE | `/{id}` | 删除模板 |
| POST | `/{id}/analyze` | AI分析模板 |

### 报告生成 API

**基础路径**: `/api/reports`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/generate` | 生成报告 |
| GET | `/` | 获取报告列表 |
| GET | `/{id}` | 获取报告详情 |
| GET | `/{id}/status` | 查询生成状态 |
| PUT | `/{id}` | 更新报告 |
| DELETE | `/{id}` | 删除报告 |

## ⚙️ 配置说明

### 环境变量

在 `.env` 文件中配置以下参数：

```env
# AI提供商选择
AI_PROVIDER=openai

# API密钥（必填）
AI_API_KEY=your_api_key

# API基础URL
AI_BASE_URL=https://api.openai.com/v1

# 模型名称
AI_MODEL=gpt-4o-mini

# 超时设置
AI_TIMEOUT=60

# 最大Token数
AI_MAX_TOKENS=4096
```

### 支持的AI提供商

| 提供商 | AI_PROVIDER | AI_BASE_URL |
|--------|-------------|-------------|
| OpenAI | openai | https://api.openai.com/v1 |
| Claude | claude | https://api.anthropic.com |
| DeepSeek | deepseek | https://api.deepseek.com |

## 📊 数据模型

### Template 模型

```python
class Template(Base):
    id: int                    # 主键
    name: str                  # 模板名称
    description: str           # 描述
    file_id: int               # 关联文件
    user_id: int               # 创建者
    content: Text              # 模板内容
    structure: JSON            # AI分析结果
    status: Enum               # 状态
    created_at: DateTime       # 创建时间
    analyzed_at: DateTime      # 分析时间
```

### Report 模型

```python
class Report(Base):
    id: int                    # 主键
    title: str                 # 标题
    template_id: int           # 模板ID
    data_file_id: int          # 数据文件ID
    user_id: int               # 创建者
    content: JSON              # 报告内容（按章节）
    full_text: Text            # 完整文本
    output_file_id: int        # 输出文件
    generation_params: JSON    # 生成参数
    status: Enum               # 状态
    progress: int              # 进度(0-100)
    created_at: DateTime       # 创建时间
    completed_at: DateTime     # 完成时间
```

## 🚀 使用示例

### 1. 创建并分析模板

```python
# 1. 创建模板
POST /api/templates
{
    "name": "光伏发电分析报告模板",
    "description": "用于光伏发电分析",
    "content": "模板文本内容..."
}

# 2. AI分析模板
POST /api/templates/{template_id}/analyze
{
    "force_reanalyze": false
}

# 响应包含结构化的模板分析结果
```

### 2. 生成报告

```python
# 生成报告
POST /api/reports/generate
{
    "template_id": 1,
    "title": "2024年Q1光伏发电分析报告",
    "data_file_id": 5,
    "custom_data": {...},
    "requirements": "强调数据可视化",
    "temperature": 0.7
}

# 查询生成状态
GET /api/reports/{report_id}/status

# 获取完成的报告
GET /api/reports/{report_id}
```

## 🔄 工作流程

### 模板分析流程

```
1. 用户上传模板文件
   ↓
2. 系统提取文本内容
   ↓
3. 调用TemplateAnalyzer
   ↓
4. AI分析模板结构
   ↓
5. 保存结构化结果到数据库
   ↓
6. 返回分析结果给用户
```

### 报告生成流程

```
1. 用户选择模板和数据
   ↓
2. 验证模板已分析完成
   ↓
3. 创建报告记录（状态:pending）
   ↓
4. 后台任务：逐章节生成内容
   ↓
5. 更新进度和状态
   ↓
6. 保存完整报告
   ↓
7. 生成文档文件
```

## 🛠️ 扩展指南

### 添加新的AI功能

1. **创建新的服务类**
```python
# app/services/ai/your_service.py
from app.services.ai.base import get_ai_client

class YourService:
    def __init__(self):
        self.ai_client = get_ai_client()
    
    async def your_method(self):
        # 实现你的功能
        pass
```

2. **在 `__init__.py` 中导出**
```python
from app.services.ai.your_service import YourService
__all__ = [..., 'YourService']
```

3. **创建对应的API端点**

### 添加新的AI提供商

1. **继承 AIClientBase**
```python
# app/services/ai/base.py
class YourAIClient(AIClientBase):
    async def chat_completion(self, messages, **kwargs):
        # 实现API调用
        pass
```

2. **在工厂函数中注册**
```python
def get_ai_client():
    provider = settings.AI_PROVIDER.lower()
    if provider == "your_provider":
        return YourAIClient()
```

## 📝 开发规范

### 1. Prompt设计原则

- **明确输出格式**：始终指定期望的JSON格式
- **提供上下文**：给AI足够的背景信息
- **分步指导**：复杂任务拆分成多个步骤
- **示例驱动**：提供输入输出示例

### 2. 错误处理

- 捕获API调用异常
- 记录详细错误信息到数据库
- 提供友好的错误提示
- 支持重试机制

### 3. 性能优化

- 使用异步调用
- 实现请求缓存
- 控制Token使用
- 并发限流

## 🔐 安全建议

1. **API密钥管理**
   - 存储在环境变量中
   - 不提交到版本控制
   - 定期轮换密钥

2. **输入验证**
   - 验证用户输入
   - 限制文件大小
   - 过滤敏感信息

3. **访问控制**
   - 基于用户权限
   - API调用频率限制
   - 审计日志记录

## 🧪 测试

### 单元测试

```python
# tests/test_template_analyzer.py
async def test_analyze_template():
    analyzer = TemplateAnalyzer()
    result = await analyzer.analyze_template(
        template_content="...",
        template_name="测试模板"
    )
    assert "报告名称" in result
```

### API测试

```bash
# 测试模板分析
curl -X POST http://localhost:8000/api/templates/1/analyze \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json"
```

## 📚 后续开发计划

- [ ] 实现后台任务队列（Celery/RQ）
- [ ] 添加更多AI提供商支持
- [ ] 实现流式输出
- [ ] 添加生成进度WebSocket推送
- [ ] 支持多语言报告生成
- [ ] 集成数据可视化
- [ ] 报告质量评估系统

## 💡 最佳实践

1. **模块化设计**：每个功能独立封装
2. **接口统一**：使用基类定义标准接口
3. **配置驱动**：通过环境变量控制行为
4. **文档完善**：代码注释和API文档
5. **日志记录**：记录关键操作和错误

---

**版本**: v1.0.0  
**最后更新**: 2025-11-03  
**维护者**: AIReportLab Team
