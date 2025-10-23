<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <h2>AIReportLab IMS</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ userStore.userInfo?.username }}</span>
        <el-button type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="dashboard-main">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="statistics-row">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <el-icon class="stat-icon" color="#409EFF"><Files /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ fileStore.statistics.total_files }}</div>
                <div class="stat-label">总文件数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <el-icon class="stat-icon" color="#67C23A"><Document /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ fileStore.statistics.total_templates }}</div>
                <div class="stat-label">模板文件</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <el-icon class="stat-icon" color="#E6A23C"><Folder /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ fileStore.statistics.total_data_files }}</div>
                <div class="stat-label">数据文件</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <el-icon class="stat-icon" color="#F56C6C"><DataAnalysis /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ formatFileSize(fileStore.statistics.total_size) }}</div>
                <div class="stat-label">总存储空间</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 文件操作区 -->
      <el-card class="file-section">
        <template #header>
          <div class="card-header">
            <span>文件管理</span>
            <div class="header-actions">
              <el-select
                v-model="filterType"
                placeholder="筛选文件类型"
                clearable
                style="width: 150px; margin-right: 10px"
                @change="handleFilterChange"
              >
                <el-option label="全部文件" value="" />
                <el-option label="模板文件" value="template" />
                <el-option label="数据文件" value="data" />
                <el-option label="其他文件" value="other" />
              </el-select>
              <el-button type="primary" @click="uploadDialogVisible = true">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </div>
          </div>
        </template>

        <!-- 文件列表 -->
        <el-table
          v-loading="fileStore.loading"
          :data="fileStore.files"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column label="文件类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getFileTypeTagType(row.file_type)">
                {{ getFileTypeLabel(row.file_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="文件大小" width="120">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column label="上传时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="handleDownload(row)"
              >
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-popconfirm
                title="确定要删除此文件吗？"
                @confirm="handleDelete(row.id)"
              >
                <template #reference>
                  <el-button type="danger" size="small">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-main>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="500px"
    >
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文件类型" required>
          <el-select v-model="uploadForm.fileType" placeholder="请选择文件类型">
            <el-option label="模板文件" value="template" />
            <el-option label="数据文件" value="data" />
            <el-option label="其他文件" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="!uploadForm.file || !uploadForm.fileType"
          @click="handleUpload"
        >
          确定上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useFileStore } from '@/stores/file'
import { formatFileSize, formatDateTime, getFileTypeLabel, getFileTypeTagType } from '@/utils/format'
import type { FileType, FileInfo } from '@/types'
import type { UploadInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  Files,
  Document,
  Folder,
  DataAnalysis,
  Upload,
  Download,
  Delete,
  UploadFilled
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const fileStore = useFileStore()

const uploadDialogVisible = ref(false)
const uploading = ref(false)
const filterType = ref<FileType | ''>('')
const uploadRef = ref<UploadInstance>()

const uploadForm = reactive<{
  file: File | null
  fileType: FileType | ''
}>({
  file: null,
  fileType: '',
})

// 初始化数据
onMounted(async () => {
  await fileStore.fetchFiles()
  await fileStore.fetchStatistics()
})

// 退出登录
const handleLogout = () => {
  userStore.logout()
}

// 筛选文件类型
const handleFilterChange = async () => {
  if (filterType.value) {
    await fileStore.fetchFiles(filterType.value as FileType)
  } else {
    await fileStore.fetchFiles()
  }
}

// 文件选择
const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 上传文件
const handleUpload = async () => {
  if (!uploadForm.file || !uploadForm.fileType) {
    ElMessage.warning('请选择文件类型和文件')
    return
  }

  uploading.value = true
  try {
    await fileStore.uploadFile(uploadForm.file, uploadForm.fileType as FileType)
    uploadDialogVisible.value = false
    // 重置表单
    uploadForm.file = null
    uploadForm.fileType = ''
    uploadRef.value?.clearFiles()
  } finally {
    uploading.value = false
  }
}

// 下载文件
const handleDownload = async (file: FileInfo) => {
  await fileStore.downloadFile(file.id, file.filename)
}

// 删除文件
const handleDelete = async (fileId: number) => {
  await fileStore.deleteFile(fileId)
}
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 30px;
  height: 60px;
}

.header-left h2 {
  margin: 0;
  color: #409EFF;
  font-size: 22px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.username {
  font-size: 14px;
  color: #606266;
}

.dashboard-main {
  padding: 20px;
  overflow-y: auto;
}

.statistics-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.file-section {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>
