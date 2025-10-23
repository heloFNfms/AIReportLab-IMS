# AIReportLab IMS API 文档

## 基础信息

- 基础URL: `http://localhost:8000`
- API版本: v1

## 认证

大多数API端点需要认证。认证通过Bearer Token实现。

### 获取Token

```
POST /api/auth/login
```

请求体:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

响应:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 用户API

### 注册用户

```
POST /api/auth/register
```

请求体:
```json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password"
}
```

响应:
```json
{
  "id": 1,
  "username": "new_user",
  "email": "user@example.com"
}
```

## 文件API

### 上传文件

```
POST /api/files/upload
```

请求: 表单数据，包含文件

响应:
```json
{
  "id": 1,
  "filename": "uploaded_file.pdf",
  "file_path": "/uploads/user_1/uploaded_file.pdf",
  "file_size": 1024,
  "file_type": "pdf",
  "created_at": "2023-11-01T12:00:00",
  "user_id": 1
}
```

### 获取用户文件列表

```
GET /api/files/
```

响应:
```json
[
  {
    "id": 1,
    "filename": "file1.pdf",
    "file_path": "/uploads/user_1/file1.pdf",
    "file_size": 1024,
    "file_type": "pdf",
    "created_at": "2023-11-01T12:00:00",
    "user_id": 1
  },
  {
    "id": 2,
    "filename": "file2.docx",
    "file_path": "/uploads/user_1/file2.docx",
    "file_size": 2048,
    "file_type": "docx",
    "created_at": "2023-11-02T14:30:00",
    "user_id": 1
  }
]
```

### 获取文件统计信息

```
GET /api/files/statistics
```

响应:
```json
{
  "total_files": 10,
  "total_templates": 3,
  "total_data_files": 7,
  "total_size": 10485760
}
```

### 获取单个文件信息

```
GET /api/files/{file_id}
```

响应:
```json
{
  "id": 1,
  "filename": "file1.pdf",
  "file_path": "/uploads/user_1/file1.pdf",
  "file_size": 1024,
  "file_type": "pdf",
  "created_at": "2023-11-01T12:00:00",
  "user_id": 1
}
```

### 下载文件

```
GET /api/files/{file_id}/download
```

响应: 文件内容

### 删除文件

```
DELETE /api/files/{file_id}
```

响应:
```json
{
  "message": "File deleted successfully"
}
```

## 错误处理

所有API错误将返回适当的HTTP状态码和JSON响应，包含错误消息。

例如:

```json
{
  "detail": "User already exists"
}
```

## 测试API

可以使用Postman或curl测试这些API端点。

示例curl命令:

```bash
# 注册用户
curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 登录获取token
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"testuser","password":"password123"}'

# 上传文件 (需要token)
curl -X POST http://localhost:8000/api/files/upload -H "Authorization: Bearer YOUR_TOKEN" -F "file=@/path/to/your/file.pdf"

# 获取文件列表
curl -X GET http://localhost:8000/api/files/ -H "Authorization: Bearer YOUR_TOKEN"
```