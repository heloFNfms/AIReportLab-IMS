# AIReportLab IMS - 用户信息管理系统

一个基于现代Web技术栈的用户信息管理系统，支持用户注册登录、文件管理等功能。

## 项目概述

AIReportLab IMS 是一个全栈Web应用，主要用于管理用户账户和文件存储，支持扩展到报告生成（如模板+数据文件处理）。

### 核心功能

- ✅ 用户注册与登录（JWT认证）
- ✅ 文件上传、下载、删除
- ✅ 文件分类管理（模板、数据、其他）
- ✅ 文件统计信息
- ✅ 响应式现代化UI

## 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: MySQL
- **ORM**: SQLAlchemy
- **认证**: JWT (python-jose)
- **密码加密**: Passlib + Bcrypt
- **数据迁移**: Alembic

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 项目结构

```
AIReportLab IMS/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── db/          # 数据库配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic模式
│   │   ├── services/    # 业务逻辑
│   │   └── main.py      # 应用入口
│   ├── migrations/      # 数据库迁移
│   ├── uploads/         # 文件上传目录
│   ├── requirements.txt # Python依赖
│   └── run_backend.py   # 启动脚本
│
└── frontend/            # 前端代码
    ├── src/
    │   ├── api/        # API接口
    │   ├── stores/     # 状态管理
    │   ├── views/      # 页面组件
    │   ├── router/     # 路由配置
    │   ├── types/      # 类型定义
    │   └── utils/      # 工具函数
    ├── package.json    # Node依赖
    └── vite.config.ts  # Vite配置
```

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 后端启动

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境变量**

复制 `.env` 文件并修改配置：
```bash
cp template.env .env
```

编辑 `.env` 文件，配置数据库连接：
```
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/aireportlab_db
SECRET_KEY=你的密钥
```

3. **创建数据库**
```sql
CREATE DATABASE aireportlab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **运行数据库迁移**
```bash
alembic upgrade head
```

5. **启动后端服务**
```bash
python run_backend.py
```

后端将运行在 `http://localhost:8000`

API文档：`http://localhost:8000/docs`

### 前端启动

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

前端将运行在 `http://localhost:3000`

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |

### 文件管理接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/files/upload | 上传文件 | ✅ |
| GET | /api/files/ | 获取文件列表 | ✅ |
| GET | /api/files/statistics | 获取统计信息 | ✅ |
| GET | /api/files/{file_id} | 获取文件信息 | ✅ |
| GET | /api/files/{file_id}/download | 下载文件 | ✅ |
| DELETE | /api/files/{file_id} | 删除文件 | ✅ |

## 数据库设计

### users 表
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- hashed_password: 加密密码
- is_active: 是否激活
- created_at: 创建时间
- updated_at: 更新时间

### files 表
- id: 主键
- filename: 文件名
- file_path: 文件路径
- file_type: 文件类型（template/data/other）
- file_size: 文件大小（字节）
- mime_type: MIME类型
- user_id: 用户ID（外键）
- created_at: 创建时间
- updated_at: 更新时间

## 安全特性

- ✅ JWT Token 认证
- ✅ 密码 Bcrypt 加密
- ✅ CORS 跨域配置
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ 文件大小限制（默认10MB）
- ✅ 用户文件隔离存储

## 开发说明

### 后端开发

- 使用 FastAPI 的依赖注入系统
- 遵循 RESTful API 设计规范
- 使用 Pydantic 进行数据验证
- 异步文件上传处理

### 前端开发

- 使用 Vue 3 Composition API
- TypeScript 类型安全
- 统一的错误处理
- 响应式设计

## 部署说明

### 后端部署

1. 使用 Gunicorn + Uvicorn 部署
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

2. 配置 Nginx 反向代理

### 前端部署

1. 构建生产版本
```bash
npm run build
```

2. 将 `dist` 目录部署到静态文件服务器

## 常见问题

### 1. 数据库连接失败
- 检查 MySQL 服务是否启动
- 检查 `.env` 文件中的数据库配置
- 确保数据库已创建

### 2. 跨域问题
- 后端已配置 CORS，允许所有来源
- 生产环境建议限制具体域名

### 3. Token 过期
- Token 默认 30 分钟过期
- 需要重新登录获取新 Token

### 4. 文件上传失败
- 检查文件大小是否超过 10MB
- 检查上传目录权限
- 查看后端日志

## 后续扩展

- [ ] 报告生成功能
- [ ] 用户权限管理
- [ ] 文件预览功能
- [ ] 批量文件操作
- [ ] 文件分享功能
- [ ] 操作日志记录

## License

MIT

## 联系方式

如有问题，请联系开发团队。
