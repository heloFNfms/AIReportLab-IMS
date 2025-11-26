<template>
  <div class="dashboard-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <!-- 顶部导航栏 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <div class="logo-icon">
          <el-icon :size="24"><DataAnalysis /></el-icon>
        </div>
        <h2>AIReportLab IMS</h2>
      </div>
      <div class="header-right">
        <div class="user-profile">
          <el-avatar :size="32" class="user-avatar">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}</el-avatar>
          <span class="username">{{ userStore.userInfo?.username }}</span>
        </div>
        <el-switch
          v-model="isDark"
          inline-prompt
          style="--el-switch-on-color: var(--brand-primary); --el-switch-off-color: var(--text-tertiary)"
          active-text="暗色"
          inactive-text="明亮"
          class="theme-switch"
        />
        <el-button type="danger" plain size="small" @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="dashboard-main">
      <!-- 统计卡片 -->
      <el-row v-if="!statsLoading" :gutter="24" class="statistics-row">
        <el-col :xs="24" :sm="12" :md="6" v-for="(item, index) in statItems" :key="index">
          <div class="stat-card" :class="`stat-card-${index + 1}`" :style="{ animationDelay: `${index * 0.1}s` }">
            <div class="card-glass-effect"></div>
            <div class="stat-icon-wrapper">
              <el-icon class="stat-icon"><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
            <div class="stat-bg-icon"><component :is="item.icon" /></div>
            <div class="card-shine"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 文件操作区 -->
      <div class="file-section">
        <div class="section-header">
          <div class="section-title">
            <span class="title-text">文件管理</span>
            <span class="title-decoration"></span>
          </div>
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
            <el-button type="primary" class="upload-btn" @click="uploadDialogVisible = true">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </div>
        </div>

        <!-- 文件列表 -->
        <div class="table-container">
          <template v-if="fileStore.files.length > 0">
            <el-table
              v-loading="fileStore.loading"
              :data="pagedFiles"
              style="width: 100%"
              class="custom-table"
              :header-cell-style="{ background: 'transparent' }"
              :row-class-name="tableRowClassName"
            >
              <el-table-column prop="filename" label="文件名" min-width="200">
                <template #default="{ row }">
                  <div class="filename-cell">
                    <div class="file-icon-wrapper" :class="getFileIconClass(row.file_type)">
                      <el-icon class="file-icon"><Document /></el-icon>
                    </div>
                    <span>{{ row.filename }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="存储位置" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.is_oss ? 'success' : 'info'" size="small" effect="light" round class="location-tag">
                    <el-icon style="margin-right: 4px;">
                      <component :is="row.is_oss ? CloudUpload : Monitor" />
                    </el-icon>
                    {{ row.is_oss ? '云端' : '本地' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="文件类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getFileTypeTagType(row.file_type)" effect="plain" round class="type-tag">
                    {{ getFileTypeLabel(row.file_type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="文件大小" width="120">
                <template #default="{ row }">
                  <span class="file-size">{{ formatFileSize(row.file_size) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="上传时间" width="180">
                <template #default="{ row }">
                  <span class="upload-time">{{ formatDateTime(row.created_at) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <div class="action-buttons">
                    <el-button
                      type="primary"
                      link
                      size="small"
                      class="action-btn download-btn"
                      @click="handleDownload(row)"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                    <el-popconfirm
                      title="确定要删除此文件吗？"
                      confirm-button-text="删除"
                      cancel-button-text="取消"
                      confirm-button-type="danger"
                      @confirm="handleDelete(row.id)"
                    >
                      <template #reference>
                        <el-button type="danger" link size="small" class="action-btn delete-btn">
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                background
                :current-page="currentPage"
                :page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                :total="totalFiles"
                @current-change="handlePageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </template>
          <template v-else>
            <div class="empty-state">
              <el-empty description="暂无文件">
                <template #image>
                  <div class="empty-icon-wrapper">
                    <el-icon class="empty-icon"><Folder /></el-icon>
                  </div>
                </template>
                <el-button type="primary" @click="uploadDialogVisible = true" class="upload-btn">
                  <el-icon><Upload /></el-icon>
                  立即上传
                </el-button>
              </el-empty>
            </div>
          </template>
        </div>
      </div>
    </el-main>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="500px"
      class="upload-dialog"
      align-center
    >
      <el-form :model="uploadForm" label-position="top">
        <el-form-item label="存储方式" required>
          <div class="storage-options">
            <div 
              class="storage-option" 
              :class="{ active: uploadForm.storageType === 'local' }"
              @click="uploadForm.storageType = 'local'"
            >
              <div class="storage-icon-wrapper local">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="option-content">
                <span class="option-title">本地存储</span>
                <span class="option-desc">存储在服务器本地磁盘</span>
              </div>
              <div class="option-check" v-if="uploadForm.storageType === 'local'">
                <el-icon><Check /></el-icon>
              </div>
            </div>
            <div 
              class="storage-option" 
              :class="{ active: uploadForm.storageType === 'oss' }"
              @click="uploadForm.storageType = 'oss'"
            >
              <div class="storage-icon-wrapper oss">
                <el-icon><Cloudy /></el-icon>
              </div>
              <div class="option-content">
                <span class="option-title">云端存储 (OSS)</span>
                <span class="option-desc">阿里云OSS，访问更快</span>
              </div>
              <div class="option-check" v-if="uploadForm.storageType === 'oss'">
                <el-icon><Check /></el-icon>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="文件类型" required>
          <el-select v-model="uploadForm.fileType" placeholder="请选择文件类型" style="width: 100%">
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
            class="upload-area"
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
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="uploading"
            :disabled="!uploadForm.file || !uploadForm.fileType"
            @click="handleUpload"
            class="confirm-btn"
          >
            确定上传
          </el-button>
        </div>
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
  Monitor,
  SwitchButton,
  Check
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

// 统计数据计算属性
const statItems = computed(() => [
  { icon: Files, value: fileStore.statistics.total_files, label: '总文件数' },
  { icon: Document, value: fileStore.statistics.total_templates, label: '模板文件' },
  { icon: Folder, value: fileStore.statistics.total_data_files, label: '数据文件' },
  { icon: DataAnalysis, value: formatFileSize(fileStore.statistics.total_size), label: '总存储空间' }
])

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

const tableRowClassName = ({ rowIndex }: { rowIndex: number }) => {
  return 'table-row-animate'
}

const getFileIconClass = (type: string) => {
  switch (type) {
    case 'template': return 'icon-template'
    case 'data': return 'icon-data'
    default: return 'icon-other'
  }
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
  position: relative;
  overflow: hidden;
}

.background-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
}

.shape-1 {
  top: -20%;
  right: -10%;
  width: 800px;
  height: 800px;
  background: var(--brand-gradient-start);
  animation: float 15s infinite ease-in-out;
}

.shape-2 {
  bottom: -20%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: var(--brand-gradient-end);
  animation: float 20s infinite ease-in-out reverse;
}

.shape-3 {
  top: 40%;
  left: 30%;
  width: 400px;
  height: 400px;
  background: var(--brand-gradient-mid);
  opacity: 0.2;
  animation: pulse 10s infinite ease-in-out;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-overlay);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: var(--glass-border);
  padding: 0 var(--space-24);
  height: 70px;
  z-index: 10;
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-12);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  border-radius: 12px;
  box-shadow: var(--shadow-glow);
  color: white;
}

.header-left h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(90deg, var(--brand-primary-dark), var(--brand-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

:root.dark .header-left h2 {
  background: linear-gradient(90deg, #fff, #ccc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-16);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: var(--shadow-sm);
}

:root.dark .user-profile {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark .user-profile:hover {
  background: rgba(0, 0, 0, 0.4);
}

.user-avatar {
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  font-weight: 600;
  border: 2px solid white;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.logout-btn {
  border-radius: 50%;
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  transform: rotate(90deg);
  background-color: #fef2f2;
}

.dashboard-main {
  padding: var(--space-24);
  overflow-y: auto;
  z-index: 1;
}

.statistics-row {
  margin-bottom: var(--space-24);
}

.stat-card {
  padding: 24px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  background: var(--bg-card);
  border: var(--glass-border);
  box-shadow: var(--shadow-sm);
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  animation: fadeIn 0.6s ease-out backwards;
}

.card-glass-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
  z-index: 0;
}

.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-20deg);
  transition: left 0.5s;
  z-index: 1;
}

.stat-card:hover .card-shine {
  left: 200%;
  transition: left 1s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: var(--shadow-xl);
}

/* Colorful Card Variants */
.stat-card-1 {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-left: 4px solid #3b82f6;
}
.stat-card-1:hover {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-card-2 {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, rgba(236, 72, 153, 0.1) 100%);
  border-left: 4px solid #ec4899;
}
.stat-card-2:hover {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
}

.stat-card-3 {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.1) 100%);
  border-left: 4px solid #10b981;
}
.stat-card-3:hover {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.stat-card-4 {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-left: 4px solid #8b5cf6;
}
.stat-card-4:hover {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
  background: white;
  box-shadow: var(--shadow-sm);
}

.stat-card:hover .stat-icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  transform: scale(1.1) rotate(5deg);
}

.stat-card-1 .stat-icon-wrapper { color: #3b82f6; }
.stat-card-2 .stat-icon-wrapper { color: #ec4899; }
.stat-card-3 .stat-icon-wrapper { color: #10b981; }
.stat-card-4 .stat-icon-wrapper { color: #8b5cf6; }

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
  transition: color 0.3s ease;
}

.stat-card:hover .stat-value {
  color: white;
}

.stat-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 4px;
  transition: color 0.3s ease;
}

.stat-card:hover .stat-label {
  color: rgba(255, 255, 255, 0.9);
}

.stat-bg-icon {
  position: absolute;
  right: -20px;
  bottom: -20px;
  font-size: 140px;
  opacity: 0.05;
  transform: rotate(-15deg);
  pointer-events: none;
  color: var(--text-primary);
  transition: all 0.5s ease;
  z-index: 1;
}

.stat-card:hover .stat-bg-icon {
  transform: rotate(0deg) scale(1.2);
  opacity: 0.1;
  color: white;
}

.file-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: var(--glass-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 300px);
  min-height: 500px;
  animation: slideUp 0.8s ease-out backwards;
  animation-delay: 0.2s;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.3);
}

:root.dark .section-header {
  background: rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.title-decoration {
  width: 40px;
  height: 4px;
  background: linear-gradient(90deg, var(--brand-primary), var(--brand-gradient-end));
  border-radius: 2px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-select {
  width: 160px;
}

.upload-btn {
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-light) 100%);
  border: none;
  font-weight: 600;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  padding: 10px 20px;
  height: auto;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.table-container {
  flex: 1;
  padding: 0 24px 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.custom-table) {
  background: transparent;
  --el-table-border-color: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-row-hover-bg-color: transparent;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}

/* Animated Table Rows */
:deep(.table-row-animate) {
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.3);
  margin-bottom: 8px;
  border-radius: 12px;
}

:deep(.table-row-animate:hover) {
  background: white !important;
  transform: scale(1.01) translateX(4px);
  box-shadow: var(--shadow-md);
  z-index: 1;
  position: relative;
}

:root.dark :deep(.table-row-animate:hover) {
  background: rgba(255, 255, 255, 0.05) !important;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.file-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.3s ease;
}

.icon-template { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.icon-data { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.icon-other { background: rgba(107, 114, 128, 0.1); color: #6b7280; }

:deep(.table-row-animate:hover) .file-icon-wrapper {
  transform: scale(1.1);
}

.file-size, .upload-time {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
  color: var(--text-tertiary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 16px 0;
}

:deep(.el-table td.el-table__cell) {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color-light);
}

:deep(.el-table__row:last-child td.el-table__cell) {
  border-bottom: none;
}

.action-buttons {
  display: flex;
  gap: 8px;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

:deep(.table-row-animate:hover) .action-buttons {
  opacity: 1;
}

.action-btn {
  padding: 4px 8px;
  border-radius: 6px;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.download-btn { color: var(--brand-primary); }
.delete-btn { color: #ef4444; }

.pagination-container {
  margin-top: auto;
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border-color);
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon-wrapper {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(236, 72, 153, 0.05));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  animation: float 6s infinite ease-in-out;
}

.empty-icon {
  font-size: 64px;
  color: var(--text-tertiary);
  opacity: 0.5;
}

/* 上传对话框样式 */
.storage-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 8px;
}

.storage-option {
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  position: relative;
  transition: all 0.3s ease;
  background: var(--bg-page);
}

.storage-option:hover {
  border-color: var(--brand-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.storage-option.active {
  border-color: var(--brand-primary);
  background: rgba(59, 130, 246, 0.05);
}

.storage-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 4px;
}

.storage-icon-wrapper.local { background: rgba(107, 114, 128, 0.1); color: #6b7280; }
.storage-icon-wrapper.oss { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }

.storage-option.active .storage-icon-wrapper {
  background: var(--brand-primary);
  color: white;
  transform: scale(1.1);
}

.option-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.option-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.option-check {
  position: absolute;
  top: 12px;
  right: 12px;
  color: var(--brand-primary);
  background: white;
  border-radius: 50%;
  padding: 2px;
  box-shadow: var(--shadow-sm);
}

:deep(.upload-area .el-upload-dragger) {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  transition: all 0.3s ease;
  padding: 40px;
}

:deep(.upload-area .el-upload-dragger:hover) {
  border-color: var(--brand-primary);
  background: rgba(59, 130, 246, 0.05);
  transform: scale(1.02);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.confirm-btn {
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-light) 100%);
  border: none;
  font-weight: 600;
  padding: 10px 24px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 0 var(--space-16);
    height: 60px;
  }
  
  .header-left h2 {
    display: none;
  }
  
  .dashboard-main {
    padding: var(--space-16);
  }
  
  .stat-card {
    margin-bottom: var(--space-12);
    height: auto;
    padding: 20px;
  }
  
  .file-section {
    height: auto;
    min-height: auto;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .filter-select, .upload-btn {
    width: 100%;
  }
  
  .storage-options {
    grid-template-columns: 1fr;
  }
}
</style>
