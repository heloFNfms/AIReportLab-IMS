# 快速启动指南

本指南帮助您快速启动 AIReportLab IMS 项目。

## 步骤 1：环境准备

### 1.1 确认已安装以下软件

- **Python 3.8+**: 运行 `python --version` 检查
- **Node.js 16+**: 运行 `node --version` 检查
- **MySQL 5.7+**: 运行 `mysql --version` 检查
- **npm**: 运行 `npm --version` 检查

### 1.2 克隆或打开项目

```bash
cd "d:/课程资料及作业/编程实训/AIReportLab IMS"
```

## 步骤 2：启动后端

### 2.1 进入后端目录

```bash
cd backend
```

### 2.2 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

### 2.4 配置数据库

**创建数据库:**

打开 MySQL 客户端，执行：
```sql
CREATE DATABASE aireportlab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**检查 .env 文件:**

确保 `backend/.env` 文件中的数据库配置正确：
```
DATABASE_URL=mysql+pymysql://root:WZY216814wzy@localhost:3306/aireportlab_db
```

如果需要修改用户名和密码，请编辑此文件。

### 2.5 运行数据库迁移

```bash
alembic upgrade head
```

### 2.6 启动后端服务

```bash
python run_backend.py
```

✅ 后端启动成功！访问 http://localhost:8000/docs 查看API文档

## 步骤 3：启动前端

### 3.1 打开新的终端窗口

保持后端运行，打开新终端。

### 3.2 进入前端目录

```bash
cd "d:/课程资料及作业/编程实训/AIReportLab IMS/frontend"
```

### 3.3 安装依赖

```bash
npm install
```

> 注意：首次安装可能需要几分钟，请耐心等待。

### 3.4 启动前端开发服务器

```bash
npm run dev
```

✅ 前端启动成功！访问 http://localhost:3000

## 步骤 4：测试系统

### 4.1 注册新用户

1. 打开浏览器访问 http://localhost:3000
2. 点击"立即注册"
3. 填写用户名、邮箱和密码
4. 点击"注册"按钮

### 4.2 登录系统

1. 使用刚注册的用户名和密码登录
2. 成功后会自动跳转到文件管理页面

### 4.3 测试文件上传

1. 点击"上传文件"按钮
2. 选择文件类型（模板/数据/其他）
3. 拖拽或选择文件
4. 点击"确定上传"

### 4.4 测试其他功能

- ✅ 查看文件列表
- ✅ 筛选文件类型
- ✅ 下载文件
- ✅ 删除文件
- ✅ 查看统计信息

## 常见问题解决

### Q1: 后端启动失败 - 数据库连接错误

**问题**: `Can't connect to MySQL server`

**解决**:
1. 确认 MySQL 服务已启动
2. 检查 `.env` 文件中的数据库配置
3. 确认数据库用户名和密码正确
4. 确认数据库 `aireportlab_db` 已创建

### Q2: 前端安装依赖失败

**问题**: `npm install` 出错

**解决**:
1. 删除 `node_modules` 目录和 `package-lock.json` 文件
2. 运行 `npm cache clean --force`
3. 重新运行 `npm install`

### Q3: 前端无法连接后端

**问题**: 登录或上传文件时报错

**解决**:
1. 确认后端服务正在运行（http://localhost:8000）
2. 检查浏览器控制台是否有跨域错误
3. 确认 `frontend/.env.development` 中的 API 地址正确

### Q4: Token 过期

**问题**: 操作时提示"未授权，请重新登录"

**解决**:
1. Token 默认 30 分钟过期
2. 重新登录即可获取新 Token

### Q5: 文件上传失败

**问题**: "文件大小超过限制"

**解决**:
1. 默认文件大小限制为 10MB
2. 如需修改，编辑 `backend/.env` 文件中的 `MAX_FILE_SIZE`

## 项目结构一览

```
AIReportLab IMS/
├── backend/                    # 后端 (FastAPI)
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── main.py            # 主应用
│   ├── .env                   # 环境配置
│   ├── requirements.txt       # Python 依赖
│   └── run_backend.py         # 启动脚本
│
└── frontend/                   # 前端 (Vue 3)
    ├── src/
    │   ├── api/               # API 请求
    │   ├── views/             # 页面组件
    │   ├── stores/            # 状态管理
    │   └── router/            # 路由配置
    ├── package.json           # Node 依赖
    └── vite.config.ts         # Vite 配置
```

## 下一步

🎉 恭喜！您已成功启动 AIReportLab IMS 系统。

现在您可以：
- 📝 查看 `README.md` 了解更多功能
- 📚 访问 http://localhost:8000/docs 查看完整 API 文档
- 🔧 根据需求修改配置和扩展功能
- 🚀 开始开发新功能

## 停止服务

**停止后端**: 在后端终端按 `Ctrl + C`

**停止前端**: 在前端终端按 `Ctrl + C`

---

如有其他问题，请查看 `README.md` 或联系开发团队。
