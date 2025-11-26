## 结论与现状核查
- 前后端整体功能链路已打通：模板分析 → 报告分段生成 → 前端轮询展示，API 使用真实接口，AI 密钥通过环境变量管理（未硬编码）。
- 但存在关键可靠性与去硬编码问题，需修正后才可称为“完全实现且真实可靠”。

## 发现的问题
1. 模板 ID 与文件 ID 混用（前端）
- `Dashboard.vue` 直接用文件 ID 调用模板分析与报告生成：`analyzeTemplate(selectedTemplateFile.value.id)`、`generateReport({ template_id: selectedTemplateFile.value!.id, ... })`
- 后端 `reports.generate` 需要真实的 `Template.id`，且模板需先分析完成（`backend/app/api/endpoints/reports.py:58-63`）。目前会导致接口失败或不可预期。

2. 服务器内部请求绕经受保护的下载端点（后端）
- 模板分析与报告任务在读取 OSS 文件时，使用 `httpx` 访问受鉴权的 `GET /api/files/{id}/download`（`templates.py:185-206`、`reports.py:242-260`），但未携带认证头，存在 401 风险。
- 且存在半硬编码 `API_BASE_URL` 默认 `http://localhost:8000/api`，不应通过自身 API 取文件内容，应直接用 OSS 服务签名 URL 或数据库路径读取。

3. 后台任务调度方式（后端）
- 使用 `asyncio.create_task(generate_report_task(...))`（`backend/app/api/endpoints/reports.py:92-96`），在开发模式或多进程环境下，任务生存期可能不稳定。更推荐 `BackgroundTasks.add_task(...)` 或集成任务队列以提升可靠性。

4. 前端数据加载与状态管理（前端）
- 生成向导初始从 `fileStore.files` 过滤模板/数据，若未提前加载或列表较多，体验不够稳健；应按需查询对应类型文件。
- 轮询 `setInterval` 在对话框关闭时未清理，存在潜在泄漏风险。

## 已实现的接口调用（符合“非硬编码”）
- DeepSeek 客户端通过环境变量读取密钥与 BaseURL（`backend/app/services/ai/base.py:148-173`），未硬编码。
- 模板分析 API：`POST /api/templates/{id}/analyze`（`frontend/src/api/templates.ts` 与 `templates.py:185-193`）。
- 报告生成 API：`POST /api/reports/generate`（`frontend/src/api/reports.ts` 与 `reports.py:28-46, 92-96`）。
- 报告状态与详情查询：`GET /api/reports/{id}/status`、`GET /api/reports/{id}`（前端 API 已封装）。

## 改造计划（去硬编码 + 提升稳健性）
### 前端
1. 新增“从文件创建模板”步骤：
- 选择模板文件后，调用 `POST /api/templates/` 创建模板（携带 `name` 与 `file_id`）。
- 获取返回的 `template.id`，再调用 `POST /api/templates/{id}/analyze`；用返回的 `structure` 驱动后续。
2. 报告生成改为使用真实 `template.id`：
- `generateReport({ template_id: template.id, data_file_id, ... })`。
3. 文件列表获取改为按类型查询：
- 使用 `GET /api/files?file_type=template` / `data` 替代直接过滤。
4. 轮询清理：
- 在对话框关闭或生成完成时清理定时器，防止资源泄漏。

### 后端
1. 读取文件内容方式调整：
- 本地文件：直接读取数据库记录中的 `file_path`。
- OSS 文件：使用 `oss_service.get_file_url(oss_path)` 获取签名 URL；用 `httpx` 直接访问签名 URL，而不是绕经自身受保护 API；不再依赖 `API_BASE_URL`。
2. 报告任务调度：
- 使用 `BackgroundTasks.add_task(generate_report_task, report_id)`；任务内使用数据库 `SessionLocal()`，并妥善关闭连接。
3. 异常与进度：
- 对每章失败记录 `error_message` 并终止；完成后设定 `completed_at`。

### 验证
- 用一个模板文件（`txt/docx`）+ 一个数据文件（`json/txt`）跑全流程：创建模板→分析→发起生成→轮询到完成→展示全文。
- 验证 OSS 与本地文件两种存储均可读；在浅/暗色模式下视觉正常。

## 交付说明
- 保留现有 API 设计与数据模型；严格使用接口，不做硬编码。
- 不暴露密钥；仅读取环境变量。
- 完成上述改造后，再进行一次端到端回归，并留存测试样例以便后续演示。