# AIReportLab IMS (信息管理系统)

AIReportLab信息管理系统是一个用于管理文件和用户的后端系统，提供用户认证和文件管理功能。

## 功能特点

- 用户认证系统（注册、登录）
- 文件管理功能（上传、下载、增删查改）
- 文件统计信息
- RESTful API接口

## 技术栈

- FastAPI
- SQLAlchemy
- Alembic (数据库迁移)
- JWT认证
- MySQL数据库

## 快速开始

### 环境要求

- Python 3.8+
- MySQL

### 安装步骤

1. 克隆仓库
```
git clone https://github.com/yourusername/aireportlab-ims.git
cd aireportlab-ims
```

2. 安装依赖
```
cd backend
pip install -r requirements.txt
```

3. 配置环境变量
复制`template.env`为`.env`并根据需要修改配置

4. 创建数据库
```sql
CREATE DATABASE aireportlab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. 运行数据库迁移
```
cd backend
python -m alembic upgrade head
```

6. 启动服务器
```
python run_backend.py
```

服务器将在`http://localhost:8000`启动

## API文档

详细的API文档请参考`backend/API_DOCUMENTATION.md`

## 项目结构

```
backend/
├── alembic.ini              # Alembic配置文件
├── migrations/              # 数据库迁移脚本
├── requirements.txt         # 项目依赖
├── run_backend.py           # 启动脚本
├── uploads/                 # 文件上传目录
└── app/
    ├── main.py              # 主应用入口
    ├── api/                 # API路由
    │   ├── endpoints/       # API端点
    │   │   ├── auth.py      # 认证相关API
    │   │   └── files.py     # 文件相关API
    │   └── api.py           # API路由配置
    ├── core/                # 核心功能
    │   ├── config.py        # 配置
    │   ├── deps.py          # 依赖注入
    │   └── security.py      # 安全相关
    ├── db/                  # 数据库
    │   ├── base.py          # 基础模型
    │   └── session.py       # 数据库会话
    ├── models/              # 数据模型
    │   ├── user.py          # 用户模型
    │   └── file.py          # 文件模型
    ├── schemas/             # Pydantic模式
    │   ├── user.py          # 用户模式
    │   └── file.py          # 文件模式
    └── services/            # 业务逻辑
        ├── user_service.py  # 用户服务
        └── file_service.py  # 文件服务
```

## 许可证

MIT