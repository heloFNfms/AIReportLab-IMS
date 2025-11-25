## 现状与问题
- 样式体系：已在 `frontend/src/App.vue:10-45` 定义 CSS 变量与暗色模式，但部分组件仍直接使用硬编码颜色（如 `Dashboard.vue:475-479`）。
- 主题一致性：未将品牌主色映射到 Element Plus 变量，组件主色未与 `--brand-primary` 同步（`frontend/src/main.ts:3-5` 引入 Element Plus）。
- 内联样式：若干视图存在内联 `style`（如 `Dashboard.vue:15`、`Dashboard.vue:84-85`），不利于全局一致与维护。
- 排版与间距：字体层级、行高、间距与圆角在页面间不完全一致（`Login.vue:150-156`、`Register.vue:224-230`）。
- 深色模式：通过 `documentElement.classList.toggle('dark')` 控制，但组件内部文本与背景未全面使用变量（`Dashboard.vue:396-399`）。

## 美化与规范建议
- 设计令牌：扩充并统一 CSS 变量，采用语义变量（文本、边框、卡片、悬停、成功/警告/危险色）。
- 主题对齐：将 Element Plus 主色等变量映射到现有品牌色，保证库组件与自定义样式一致。
- 排版系统：统一标题、正文、说明的字号/字重/行高；优先用 `var(--text-primary/secondary)` 控制颜色。
- 间距与圆角：统一使用 `--space-*` 与 `--card-radius`；移除内联间距/圆角，改为类样式。
- 阴影与层次：规范 `--shadow-*` 使用，卡片/弹窗/悬浮层层次清晰且不过度。
- 交互可访问性：按钮与输入聚焦态可见、键盘导航友好、颜色对比符合 WCAG。

## 技术实现要点
- 映射 Element Plus 主题变量：在 `App.vue` 的 `:root`/`:root.dark` 增加 `--el-color-primary: var(--brand-primary)`，并补充必要浅/深阶梯变量，保持库样式一致。
- 文本颜色统一：将 `.stat-value/.stat-label/.username` 等硬编码颜色改为 `var(--text-primary/secondary)`（`Dashboard.vue:475-483`、`Dashboard.vue:436-438`）。
- 移除内联样式：把 `el-switch`、`el-select` 等的行间距/宽度内联样式迁移到类选择器（如 `Dashboard.vue:15` 的 `margin-right`、`Dashboard.vue:84-85` 的宽度间距）。
- 登录/注册美化：
  - 背景采用更柔和的分层（渐变+轻微噪点或玻璃拟态），盒子使用 `backdrop-filter` 与变量控制的暗色背景（`Login.vue:146`、`Register.vue:221`）。
  - 标题与说明应用统一排版规则，按钮加入细微动效与可见聚焦态（`Login.vue:162-171`、`Register.vue:237-246`）。
- 表格与标签：维持现有 `:deep` 定制，同时改用变量控制 hover/thead 背景，避免硬编码（`Dashboard.vue:504-516`）。
- 深色模式完善：确保所有文本/背景/边框使用变量；切换时同步本地存储已实现（`Dashboard.vue:396-399`、`Login.vue:133-136`、`Register.vue:208-211`）。

## 具体修改清单
1. `frontend/src/App.vue`
- 在 `:root`/`:root.dark` 增补 Element Plus 主题变量映射（`--el-color-primary` 等），完善文本/背景/边框语义变量；保留现有梯度与阴影。
2. `frontend/src/views/Dashboard.vue`
- 将 `.stat-value/.stat-label/.username` 颜色改用变量；优化 header 渐变与间距；移除 `el-switch` 与 `el-select` 的内联样式，新增类统一控制；卡片与按钮统一圆角与阴影，细化 hover/active/focus。
3. `frontend/src/views/Login.vue`
- 背景渐变优化；`login-box` 支持暗色变量背景与玻璃拟态可选；统一排版与间距；按钮聚焦/动效与无障碍改善。
4. `frontend/src/views/Register.vue`
- 与登录页保持一致的视觉与交互规范，复用变量与类，移除硬编码颜色。

## 验证与回归
- 本地启动前端，在浅色/深色模式下检查所有页面（登录/注册/仪表盘）。
- 检查 Element Plus 组件主色一致性（按钮、选择器、分页、标签等）。
- 视图在移动端与窄屏下的布局与间距表现是否稳定。
- 对比交互态（hover/focus/active）与可访问性对比度。

## 交付说明
- 不新增依赖、不创建新文件，全部在现有文件内完成样式与变量改造。
- 变更集中在 `App.vue`（主题变量）与三大视图文件；保留现有逻辑与路由/状态。