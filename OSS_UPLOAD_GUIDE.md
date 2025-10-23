# 阿里云OSS上传功能使用指南

## 📌 功能概述

系统现在支持两种文件存储方式：
1. **本地存储** - 文件保存在服务器本地磁盘
2. **云端存储（OSS）** - 文件上传到阿里云对象存储

## 🔧 配置信息

### 阿里云OSS配置
- **Bucket名称**: wang-artemis
- **区域**: 华东1（杭州）
- **Endpoint**: oss-cn-hangzhou.aliyuncs.com
- **访问URL前缀**: https://wang-artemis.oss-cn-hangzhou.aliyuncs.com

配置文件位置: `backend/app/core/config.py`

## 📡 API接口

### 1. 上传文件到本地存储
**接口**: `POST /api/files/upload`

**参数**:
- `file`: 文件（form-data）
- `file_type`: 文件类型（query参数）- template/data/other

**响应示例**:
```json
{
  "id": 1,
  "filename": "example.xlsx",
  "file_path": "./uploads/1/data/20251023/uuid.xlsx",
  "file_type": "data",
  "file_size": 12345,
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "user_id": 1,
  "is_oss": false,
  "oss_path": null,
  "oss_url": null,
  "created_at": "2025-10-23T10:00:00",
  "updated_at": "2025-10-23T10:00:00"
}
```

### 2. 上传文件到阿里云OSS
**接口**: `POST /api/files/upload-oss`

**参数**:
- `file`: 文件（form-data）
- `file_type`: 文件类型（query参数）- template/data/other

**响应示例**:
```json
{
  "id": 2,
  "filename": "example.xlsx",
  "file_path": "uploads/1/data/20251023/uuid.xlsx",
  "file_type": "data",
  "file_size": 12345,
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "user_id": 1,
  "is_oss": true,
  "oss_path": "uploads/1/data/20251023/uuid.xlsx",
  "oss_url": "https://wang-artemis.oss-cn-hangzhou.aliyuncs.com/uploads/1/data/20251023/uuid.xlsx",
  "created_at": "2025-10-23T10:00:00",
  "updated_at": "2025-10-23T10:00:00"
}
```

## 💻 前端使用方法

### 在Vue组件中使用

```vue
<script setup lang="ts">
import { useFileStore } from '@/stores/file'
import { FileType } from '@/types'

const fileStore = useFileStore()

// 上传到本地
const uploadToLocal = async (file: File) => {
  await fileStore.uploadFile(file, FileType.DATA)
}

// 上传到OSS云端
const uploadToOSS = async (file: File) => {
  await fileStore.uploadFileToOSS(file, FileType.DATA)
}
</script>
```

### 直接调用API

```typescript
import { uploadFile, uploadFileToOSS } from '@/api'
import { FileType } from '@/types'

// 上传到本地
const file = document.querySelector('input[type="file"]').files[0]
await uploadFile(file, FileType.TEMPLATE)

// 上传到OSS
await uploadFileToOSS(file, FileType.TEMPLATE)
```

## 🗄️ 数据库字段说明

### files表新增字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `is_oss` | Boolean | 是否存储在OSS（false=本地，true=OSS） |
| `oss_path` | String(500) | OSS中的文件路径 |
| `oss_url` | String(500) | OSS文件的访问URL |

## 🔐 安全说明

1. **AccessKey管理**: 
   - 生产环境建议使用RAM角色或STS临时凭证
   - 不要将AccessKey硬编码在代码中
   - 使用环境变量管理敏感信息

2. **Bucket权限**:
   - 建议配置为私有读写
   - 使用签名URL控制访问权限
   - 定期审计访问日志

## 📊 文件路径结构

### 本地存储
```
./uploads/
  └── {user_id}/
      ├── template/
      ├── data/
      └── other/
```

### OSS存储
```
uploads/
  └── {user_id}/
      └── {file_type}/
          └── {YYYYMMDD}/
              └── {uuid}.{ext}
```

## 🚀 测试步骤

1. **启动后端服务**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **启动前端服务**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **访问应用**: http://localhost:3000

4. **测试上传**:
   - 登录系统
   - 进入文件管理页面
   - 选择文件
   - 选择上传方式（本地/云端）
   - 上传文件并查看结果

## 📝 环境变量配置

在 `backend/.env` 文件中可以配置：

```env
# 阿里云OSS配置
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=wang-artemis
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_URL_PREFIX=https://wang-artemis.oss-cn-hangzhou.aliyuncs.com
```

## ⚠️ 注意事项

1. **文件大小限制**: 默认10MB，可在配置中修改
2. **OSS费用**: 注意监控OSS使用量和费用
3. **网络要求**: 上传到OSS需要服务器能访问外网
4. **文件删除**: 删除文件时会同时删除OSS中的文件
5. **迁移现有文件**: 已上传的本地文件不会自动迁移到OSS

## 🔄 数据库迁移

如果需要手动运行迁移：

```bash
cd backend
alembic upgrade head
```

回滚迁移：
```bash
alembic downgrade -1
```

## 📞 技术支持

如有问题，请查看：
- 后端日志: 查看uvicorn控制台输出
- 前端日志: 浏览器开发者工具Console
- OSS日志: 阿里云控制台 > OSS > 日志管理
