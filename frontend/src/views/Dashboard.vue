<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
  <el-header class="dashboard-header">
      <div class="header-left">
        <h2>AIReportLab IMS</h2>
      </div>
  <div class="header-right">
    <span class="username">{{ userStore.userInfo?.username }}</span>
    <el-switch
      v-model="isDark"
      inline-prompt
      active-text="暗色"
      inactive-text="明亮"
      class="theme-switch"
    />
    <el-button type="danger" @click="handleLogout">退出登录</el-button>
  </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="dashboard-main">
      <!-- 统计卡片 -->
<el-row v-if="!statsLoading" :gutter="20" class="statistics-row">
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
                class="filter-select"
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
        <template v-if="fileStore.files.length > 0">
          <el-table
            v-loading="fileStore.loading"
            :data="pagedFiles"
            stripe
            style="width: 100%"
          >
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column label="存储位置" width="110">
            <template #default="{ row }">
              <el-tag :type="row.is_oss ? 'success' : 'info'" size="small">
                <el-icon style="margin-right: 4px;">
                  <component :is="row.is_oss ? CloudUpload : Monitor" />
                </el-icon>
                {{ row.is_oss ? '云端' : '本地' }}
              </el-tag>
            </template>
          </el-table-column>
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
                class="op-btn"
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
                  <el-button type="danger" size="small" class="op-btn">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
          </el-table>
          <div style="display:flex; justify-content:flex-end; margin-top: 12px;">
            <el-pagination
              background
              :current-page="currentPage"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              layout="prev, pager, next, sizes, total"
              :total="totalFiles"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
            />
          </div>
        </template>
        <template v-else>
          <el-empty description="暂无文件">
            <el-button type="primary" @click="uploadDialogVisible = true">
              <el-icon><Upload /></el-icon>
              立即上传
            </el-button>
          </el-empty>
        </template>
      </el-card>
    </el-main>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="500px"
    >
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="存储方式" required>
          <el-select v-model="uploadForm.storageType" placeholder="请选择存储方式">
            <el-option label="本地存储" value="local">
              <div style="display: flex; flex-direction: column;">
                <span>本地存储</span>
                <span style="font-size: 12px; color: #909399;">存储在服务器本地磁盘</span>
              </div>
            </el-option>
            <el-option label="云端存储 (OSS)" value="oss">
              <div style="display: flex; flex-direction: column;">
                <span>云端存储 (OSS)</span>
                <span style="font-size: 12px; color: #909399;">存储在阿里云OSS，访问更快</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
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
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
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
import { ref, reactive, onMounted, computed, watch } from 'vue'
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
  UploadFilled,
  Cloudy,
  Monitor
} from '@element-plus/icons-vue'
const CloudUpload = Cloudy

const userStore = useUserStore()
const fileStore = useFileStore()

const uploadDialogVisible = ref(false)
const uploading = ref(false)
const filterType = ref<FileType | ''>('')
const uploadRef = ref<UploadInstance>()
const statsLoading = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const totalFiles = computed(() => fileStore.files.length)
const pagedFiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return fileStore.files.slice(start, end)
})
const isDark = ref(false)

const uploadForm = reactive<{
  file: File | null
  fileType: FileType | ''
  storageType: 'local' | 'oss'
}>({
  file: null,
  fileType: '',
  storageType: 'local',
})

// 初始化数据
onMounted(async () => {
  statsLoading.value = true
  const theme = localStorage.getItem('theme')
  isDark.value = theme === 'dark'
  document.documentElement.classList.toggle('dark', isDark.value)
  await fileStore.fetchFiles()
  await fileStore.fetchStatistics()
  statsLoading.value = false
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
    // 根据存储方式选择不同的上传方法
    if (uploadForm.storageType === 'oss') {
      await fileStore.uploadFileToOSS(uploadForm.file, uploadForm.fileType as FileType)
    } else {
      await fileStore.uploadFile(uploadForm.file, uploadForm.fileType as FileType)
    }
    uploadDialogVisible.value = false
    // 重置表单
    uploadForm.file = null
    uploadForm.fileType = ''
    uploadForm.storageType = 'local'
    uploadRef.value?.clearFiles()
  } finally {
    uploading.value = false
  }
}

// 下载文件
const handleDownload = async (file: FileInfo) => {
  // 云端文件通过后端下载接口重定向至 OSS 签名URL，避免跨域与 Blob 处理问题
  if (file.is_oss) {
    const base = import.meta.env.VITE_API_BASE_URL || '/api'
    const url = `${base}/files/${file.id}/download`
    const link = document.createElement('a')
    link.href = url
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    return
  }
  await fileStore.downloadFile(file.id, file.filename)
}

// 删除文件
const handleDelete = async (fileId: number) => {
  await fileStore.deleteFile(fileId)
}

// 分页操作
const handlePageChange = (page: number) => {
  currentPage.value = page
}
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

watch(isDark, (val) => {
  document.documentElement.classList.toggle('dark', val)
  localStorage.setItem('theme', val ? 'dark' : 'light')
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-page);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--brand-gradient-start) 0%, var(--brand-gradient-end) 100%);
  color: #fff;
  box-shadow: var(--shadow-sm);
  padding: 0 var(--space-16);
  height: 60px;
}

.header-left h2 {
  margin: 0;
  color: #fff;
  font-size: 22px;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-16);
}

.username {
  font-size: 14px;
  color: #f2f6fc;
}

.dashboard-main {
  padding: var(--space-16);
  overflow-y: auto;
}

.statistics-row {
  margin-bottom: var(--space-16);
}

.stat-card {
  cursor: pointer;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 48px;
  margin-right: var(--space-16);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.file-section {
  margin-top: var(--space-16);
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-switch {
  margin-right: var(--space-12);
}

.filter-select {
  width: 180px;
  margin-right: var(--space-8);
}

/* 细节优化：圆角与层次感（作用到子组件需要使用深度选择器） */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table thead th) {
  background: var(--table-header-bg);
  color: var(--table-header-text);
}

:deep(.el-table .el-table__row:hover) {
  background: var(--table-row-hover);
}

:deep(.el-tag) {
  border-radius: 6px;
}

:deep(.el-button.is-round),
:deep(.el-button--small) {
  border-radius: 8px;
}

.op-btn {
  transition: transform 0.2s, box-shadow 0.2s;
}
.op-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
</style>
