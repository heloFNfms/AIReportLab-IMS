# AIReportLab IMS - 前端

基于 Vue 3 + TypeScript + Vite + Element Plus 的用户信息管理系统前端。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **图标**: Element Plus Icons

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口
│   │   ├── auth.ts       # 认证相关接口
│   │   ├── files.ts      # 文件相关接口
│   │   ├── request.ts    # Axios 实例配置
│   │   └── index.ts
│   ├── stores/           # Pinia 状态管理
│   │   ├── user.ts       # 用户状态
│   │   └── file.ts       # 文件状态
│   ├── views/            # 页面组件
│   │   ├── Login.vue     # 登录页
│   │   ├── Register.vue  # 注册页
│   │   └── Dashboard.vue # 主面板（文件管理）
│   ├── types/            # TypeScript 类型定义
│   │   └── index.ts
│   ├── utils/            # 工具函数
│   │   ├── format.ts     # 格式化工具
│   │   └── validator.ts  # 验证工具
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── index.html            # HTML 模板
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
└── package.json          # 项目依赖

```

## 功能特性

### 用户认证
- ✅ 用户注册（用户名、邮箱、密码验证）
- ✅ 用户登录（JWT Token 认证）
- ✅ 自动登录（Token 持久化）
- ✅ 路由守卫（未登录重定向）

### 文件管理
- ✅ 文件上传（支持拖拽上传）
- ✅ 文件列表展示
- ✅ 文件类型筛选（模板/数据/其他）
- ✅ 文件下载
- ✅ 文件删除
- ✅ 文件统计（总数、类型、存储空间）

### UI/UX
- ✅ 响应式设计
- ✅ 现代化界面
- ✅ 加载状态提示
- ✅ 错误处理和提示
- ✅ 表单验证

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 开发环境运行

```bash
npm run dev
```

前端将运行在 `http://localhost:3000`

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 环境配置

### 开发环境 (`.env.development`)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### 生产环境 (`.env.production`)
```
VITE_API_BASE_URL=/api
```

## API 接口

前端通过 Axios 与后端 API 通信，所有接口请求都会自动：
- 添加 JWT Token（如果已登录）
- 统一错误处理
- 显示友好的错误提示

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 文件接口
- `POST /api/files/upload` - 上传文件
- `GET /api/files/` - 获取文件列表
- `GET /api/files/statistics` - 获取统计信息
- `GET /api/files/{file_id}` - 获取文件信息
- `GET /api/files/{file_id}/download` - 下载文件
- `DELETE /api/files/{file_id}` - 删除文件

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建新的 Vue 组件
2. 在 `src/router/index.ts` 添加路由配置
3. 配置路由守卫（如需认证）

### 添加新的 API

1. 在 `src/api/` 创建新的 API 模块
2. 使用 `request` 实例发送请求
3. 在 `src/api/index.ts` 导出

### 状态管理

使用 Pinia 进行状态管理：
```typescript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
userStore.login(username, password)
```

## 浏览器支持

- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

## 注意事项

1. **端口配置**: 前端默认运行在 3000 端口，后端需要在 8000 端口
2. **CORS**: 后端已配置 CORS，允许跨域请求
3. **Token 过期**: Token 默认 30 分钟过期，过期后需重新登录
4. **文件大小限制**: 默认最大上传 10MB

## 相关链接

- [Vue 3 文档](https://cn.vuejs.org/)
- [Vite 文档](https://cn.vitejs.dev/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [Pinia 文档](https://pinia.vuejs.org/zh/)
- [Vue Router 文档](https://router.vuejs.org/zh/)
