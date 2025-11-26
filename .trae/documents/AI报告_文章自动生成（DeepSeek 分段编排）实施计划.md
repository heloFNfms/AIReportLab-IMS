## 目标概述
- 在现有“模板文件/数据文件”基础上，支持 AI 自动生成报告/文章。
- 用户在前端选择模板文件与数据文件后，系统分段生成各章节内容，并最终拼接为完整报告。
- 使用 DeepSeek API；密钥通过环境变量管理，不在代码或日志中暴露。

## 用户流程
1. 在仪表盘点击“报告自动生成”。
2. 在弹窗/向导中：
   - 选择一个模板文件（`file_type=template`），点击“分析模板”得到章节结构。
   - 选择一个数据文件（`file_type=data`）。
   - 可选：填写标题、风格要求、AI参数（模型、温度）。
3. 点击“开始生成”：后端创建报告并异步生成各章节；前端轮询进度显示。
4. 生成完成后展示分章节内容与完整文本；支持下载为文本文件并归档到文件库。

## 后端实现
- AI客户端（DeepSeek）
  - 新增 `DeepSeekClient`（OpenAI 兼容协议）：`POST https://api.deepseek.com/v1/chat/completions`，`Authorization: Bearer <API_KEY>`。
  - 在工厂函数中支持 `AI_PROVIDER=deepseek` 返回 `DeepSeekClient`。
  - `.env` 示例：`AI_PROVIDER=deepseek`、`AI_API_KEY=***`、`AI_BASE_URL=https://api.deepseek.com/v1`、`AI_MODEL=deepseek-chat`、`AI_TIMEOUT=60`、`AI_MAX_TOKENS=4096`。
- 模板分析
  - 现有 `TemplateAnalyzer` 已支持分块分析（`analyze_template_in_chunks`）。
  - 补全从 `file_id` 读取文件内容逻辑（支持 `txt/docx`，本地或 OSS 通过签名URL），保存到 `Template.content` 后调用分析。
- 报告生成编排器
  - 完成 `generate_report_task`（`backend/app/api/endpoints/reports.py`）：
    - 将报告状态改为 `generating`，按 `template.structure['章节结构']` 迭代生成：
      - 对每章调用 `ReportGenerator.generate_section(...)`，并在每章结束更新 `progress`（按章节百分比）。
      - 如单章过长，按小节/字数建议进一步分块生成再拼接（控制 `AI_MAX_TOKENS`）。
    - 合并所有章节为 `full_text`；保存章节字典到 `Report.content`；若需要，写入文本文件并登记 `output_file_id`。
    - 成功后标记 `completed_at` 与 `status=completed`；异常时写入 `error_message` 与 `status=failed`。
  - 在 `/api/reports/generate` 中添加后台任务调度；返回初始报告记录供前端轮询。
- 数据抽取与映射
  - 若数据文件为 JSON：直接解析为 dict 注入 `ReportGenerator`。
  - 若为 TXT/CSV：读取文本，使用 `extract_data_from_file(data_requirements)` 结构化抽取，传入章节生成。
- 安全与配置
  - 不在代码打印或返回密钥；仅从 `settings` 读取。
  - CORS 与鉴权沿用当前实现；仅对已登录用户操作自身资源。

## 前端实现
- API 封装
  - 新增 `frontend/src/api/templates.ts`：创建、获取、分析模板（`POST /api/templates/{id}/analyze`）。
  - 新增 `frontend/src/api/reports.ts`：创建生成任务（`POST /api/reports/generate`）、列表、详情、状态轮询。
- 状态与视图
  - 新增 `Pinia` store：`useTemplateStore`（模板列表与分析）与 `useReportStore`（创建任务与进度轮询）。
  - 在 `Dashboard.vue` 新增“AI报告生成”按钮与弹窗/向导：
    - 步骤组件：选择模板文件→分析模板（显示章节预览）→选择数据文件→参数设置→启动生成→进度展示。
    - 生成完成后展示章节列表与 `full_text`；提供“保存为文本到文件库”按钮。
- 交互细节
  - 进度条与状态提示（`pending/generating/completed/failed`）。
  - 参数默认值与可选模型下拉（初期只列 `deepseek-chat`）。

## 分段编排设计
- 章节级编排：按 `Template.structure.章节结构` 循环生成，累积 `context` 用于后续章节一致性（现有实现已支持）。
- 小节/块级编排：对于字数建议很长或存在子条目时，按 `chunk_size` 分块生成，减少 token 压力；每块加入前文摘要与严格的合并规则。
- 合并策略：在后端合并时进行“过渡段润色”（`refine_content`）以保证连贯性；可设置迭代次数。

## 数据与模板支持
- 支持 `docx/txt/json/csv` 模板与数据：
  - 模板：`docx/txt` 解析文本后分析。
  - 数据：优先 JSON；非结构化文本用 `structured_output` 提取需要字段。

## 验证与测试
- 单元测试：
  - DeepSeek 客户端连通性与超时处理；模板分析返回结构的健壮性；报告编排任务的失败回退与进度更新。
- 集成测试：
  - 前端从选择→分析→生成→展示的全流程；轮询状态的可靠性；文件归档下载。

## 里程碑
1. 后端：DeepSeek 客户端与模板文件内容读取；报告后台任务完成；`/generate` 调度与状态。
2. 前端：API 封装、stores 与向导 UI；状态轮询与结果展示。
3. 数据/模板解析增强与块级编排；下载与归档。
4. 测试与性能优化（并发限流、重试策略、最大 token 控制）。

## 密钥管理说明
- 请将提供的密钥配置到 `.env`：`AI_PROVIDER=deepseek`、`AI_API_KEY=sk-...`、`AI_BASE_URL=https://api.deepseek.com/v1`、`AI_MODEL=deepseek-chat`。
- 不要将密钥硬编码到仓库或打印到日志；后端通过 `settings` 读取。