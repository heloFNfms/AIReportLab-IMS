# 环境变量配置指南

## 📋 概述

为了提高安全性，本项目使用 `.env` 文件管理所有敏感配置信息。**`.env` 文件不会被提交到 Git 仓库**。

## 🚀 快速开始

### 1. 创建 .env 文件

项目已经为你创建了 `.env` 文件，位于 `backend/.env`。

如果需要重新创建，可以复制模板文件：

```bash
cd backend
cp .env.example .env
```

### 2. 配置说明

#### 数据库配置
```env
DATABASE_URL=mysql+pymysql://root:1234@localhost:3306/aireport_ims
```
- 格式：`mysql+pymysql://用户名:密码@主机:端口/数据库名`
- 确保 MySQL 服务已启动
- 确保数据库已创建

#### JWT 安全配置
```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
- `SECRET_KEY`: JWT 加密密钥，**生产环境必须修改！**
- 生成新密钥的方法：
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

#### 文件存储配置
```env
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760
```
- `MAX_FILE_SIZE`: 单位为字节（默认 10MB = 10485760 字节）

#### 阿里云 OSS 配置
```env
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_URL_PREFIX=https://your_bucket_name.oss-cn-hangzhou.aliyuncs.com
```

**获取 OSS 配置：**
1. 登录 [阿里云控制台](https://ram.console.aliyun.com/manage/ak)
2. 创建 AccessKey
3. 创建 OSS Bucket
4. 填入对应的配置信息

#### 服务器配置
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
```
- `DEBUG`: 开发环境设为 `True`，生产环境设为 `False`

## 🔒 安全最佳实践

### ✅ 应该做的

1. **永远不要将 `.env` 文件提交到 Git**
   - `.gitignore` 已配置排除 `.env`
   - 验证：`git status` 不应显示 `.env`

2. **不同环境使用不同的配置**
   - 开发环境：`.env`
   - 生产环境：使用环境变量或密钥管理服务

3. **定期更换密钥**
   - 特别是 `SECRET_KEY` 和 OSS 密钥

4. **最小权限原则**
   - OSS 使用 RAM 子账号，限制权限
   - 只授予必要的读写权限

### ❌ 不应该做的

1. **不要在代码中硬编码敏感信息**
2. **不要在公共渠道分享 `.env` 文件**
3. **不要使用默认密钥在生产环境**

## 📝 文件说明

- **`.env`**: 实际配置文件（不提交到 Git）
- **`.env.example`**: 配置模板（提交到 Git）
- **`app/core/config.py`**: 配置加载器

## 🔄 环境变量加载流程

```
1. 应用启动
2. load_dotenv() 从 .env 读取配置
3. Settings 类加载配置
4. 应用使用 settings 对象访问配置
```

## 🛠️ 故障排除

### 问题：配置未生效

**解决方案：**
1. 确认 `.env` 文件存在于 `backend/` 目录
2. 检查文件编码是否为 UTF-8
3. 检查是否有语法错误（如多余的引号、空格）
4. 重启应用服务

### 问题：OSS 上传失败

**检查清单：**
- [ ] OSS AccessKey 是否正确
- [ ] OSS Bucket 是否存在
- [ ] OSS Endpoint 是否正确
- [ ] 网络连接是否正常

### 问题：数据库连接失败

**检查清单：**
- [ ] MySQL 服务是否启动
- [ ] 数据库是否已创建
- [ ] 用户名密码是否正确
- [ ] 主机和端口是否正确

## 📚 相关文档

- [快速开始指南](./QUICKSTART.md)
- [OSS 使用指南](./OSS_UPLOAD_GUIDE.md)
- [阿里云 OSS 文档](https://help.aliyun.com/product/31815.html)

## 🆘 需要帮助？

如果遇到问题，请检查：
1. 本文档的故障排除部分
2. 应用日志（`uvicorn` 输出）
3. `.env` 文件配置是否正确
