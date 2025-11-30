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
          <el-avatar :size="32" class="user-avatar">{{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
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
            <el-button type="warning" class="upload-btn" @click="editorDialogVisible = true">
              <el-icon><Edit /></el-icon>
              开始撰写报告
            </el-button>
            <el-button v-if="!disableAIGeneration" type="success" class="upload-btn" @click="generatorDialogVisible = true">
              <el-icon><DataAnalysis /></el-icon>
              报告自动生成
            </el-button>
            <el-button type="info" class="upload-btn" @click="openReportsDialog">
              <el-icon><DataAnalysis /></el-icon>
              查看草稿与报告
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
                      <el-icon v-if="row.file_type === 'template'"><Document /></el-icon>
                      <el-icon v-else-if="row.file_type === 'data'"><Folder /></el-icon>
                      <el-icon v-else><Files /></el-icon>
                    </div>
                    <div class="filename-text">
                      <span>{{ row.filename }}</span>
                      <el-tag v-if="row.is_oss" size="small" effect="plain" round class="oss-tag">OSS</el-tag>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="大小" width="120">
                <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间" width="180">
                <template #default="{ row }">
                  <span class="upload-time">{{ formatDateTime(row.created_at) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <div class="action-buttons">
                    <el-button link class="action-btn download-btn" @click="handleDownload(row)">
                      <el-icon><Download /></el-icon>
                    </el-button>
                    <el-popconfirm title="确定删除该文件吗？" @confirm="handleDelete(row.id)" width="200">
                      <template #reference>
                        <el-button link class="action-btn delete-btn">
                          <el-icon><Delete /></el-icon>
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
                layout="total, sizes, prev, pager, next"
                :total="totalFiles"
                :page-sizes="[10, 20, 50, 100]"
                :page-size="pageSize"
                :current-page="currentPage"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
              />
            </div>
          </template>
          
          <div v-else class="empty-state">
            <div class="empty-content">
              <div class="empty-icon-wrapper">
                <el-icon class="empty-icon"><Folder /></el-icon>
              </div>
              <p>暂无文件，请上传</p>
            </div>
          </div>
        </div>
      </div>
    </el-main>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px" align-center class="upload-dialog">
      <div class="storage-options">
        <div 
          class="storage-option" 
:class="{ active: !(userStore as any).uploadToOss }"
          @click="userStore.setUploadToOss(false)"
        >
          <div class="storage-icon-wrapper local"><el-icon><Monitor /></el-icon></div>
          <div class="option-content">
            <span class="option-title">本地存储</span>
            <span class="option-desc">存储在服务器本地磁盘</span>
          </div>
          <el-icon class="option-check" v-if="!userStore.uploadToOss"><Check /></el-icon>
        </div>
        <div 
          class="storage-option" 
          :class="{ active: userStore.uploadToOss }"
          @click="userStore.setUploadToOss(true)"
        >
          <div class="storage-icon-wrapper oss"><el-icon><CloudUpload /></el-icon></div>
          <div class="option-content">
            <span class="option-title">阿里云 OSS</span>
            <span class="option-desc">存储在云端对象存储</span>
          </div>
          <el-icon class="option-check" v-if="userStore.uploadToOss"><Check /></el-icon>
        </div>
      </div>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        action="#"
        :http-request="handleUpload"
        :auto-upload="false"
        :limit="1"
        :on-exceed="handleExceed"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持任意格式文件，单个文件不超过 500MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploading" class="confirm-btn">
            {{ uploading ? '上传中...' : '开始上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    <el-dialog 
      v-model="reportsDialogVisible" 
      title="已生成报告" 
      width="900px" 
      align-center
      class="generator-dialog"
    >
      <div class="generator-content">
        <div class="step-header">
          <el-select v-model="reportFilterStatus" style="width: 180px">
            <el-option label="全部" value="all" />
            <el-option label="已完成" value="completed" />
            <el-option label="生成中" value="generating" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-button @click="fetchReports" :loading="reportsLoading">刷新</el-button>
        </div>
        <div class="dialog-table-container">
          <el-table :data="filteredReports" v-loading="reportsLoading" class="custom-table" :header-cell-style="{ background: 'transparent' }">
            <el-table-column prop="title" label="标题" min-width="280" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status==='completed'?'success':row.status==='failed'?'danger':'primary'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="220">
              <template #default="{ row }">
                <el-progress :percentage="row.progress || 0" :status="row.status==='completed'?'success':''" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="220">
              <template #default="{ row }">
                <el-button link @click="viewReport(row)">查看</el-button>
                <el-button link @click="downloadReportRow(row)">下载</el-button>
                <el-popconfirm title="确认删除?" @confirm="deleteReportRow(row)">
                  <template #reference>
                    <el-button link type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reportsDialogVisible=false; stopAllPolls()">关闭</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 报告生成向导 -->
    <el-dialog 
      v-model="generatorDialogVisible" 
      title="AI报告自动生成" 
      width="800px" 
      align-center
      class="generator-dialog"
    >
      <el-steps :active="generatorStep" finish-status="success" align-center class="generator-steps">
        <el-step title="选择模板" />
        <el-step title="分析模板" />
        <el-step title="选择数据" />
        <el-step title="生成报告" />
      </el-steps>

      <div class="generator-content">
        <!-- Step 0: 选择模板 -->
        <div v-if="generatorStep === 0" class="step-fade-in">
          <div class="step-header">
            <div class="info-tag template">
              <el-icon><Document /></el-icon>
              <span>请选择报告模板</span>
            </div>
            <el-button size="small" circle @click="fetchTemplateFiles">
              <el-icon><Files /></el-icon>
            </el-button>
          </div>
          
          <el-alert v-if="selectedTemplateFile" type="success" :closable="false" class="selection-alert">
            <template #title>
              <div class="selected-info">
                <el-icon><Check /></el-icon>
                <span>已选择: <strong>{{ selectedTemplateFile.filename }}</strong></span>
              </div>
            </template>
          </el-alert>

          <div class="dialog-table-container">
            <el-table 
              :data="templateFiles" 
              height="300" 
              style="width:100%" 
              v-loading="generatorLoading"
              class="custom-table"
              :header-cell-style="{ background: 'transparent' }"
              :row-class-name="getTemplateRowClass"
            >
              <el-table-column prop="filename" label="模板文件" min-width="240">
                <template #default="{ row }">
                  <div class="filename-cell">
                    <div class="file-icon-wrapper icon-template" style="width: 28px; height: 28px; font-size: 14px;">
                      <el-icon><Document /></el-icon>
                    </div>
                    <span>{{ row.filename }}</span>
                    <el-tag v-if="selectedTemplateFile?.id === row.id" type="success" size="small" effect="dark" style="margin-left: auto">已选</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="大小" width="100">
                <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button 
                    :type="selectedTemplateFile?.id === row.id ? 'success' : 'primary'" 
                    size="small" 
                    link
                    @click="selectTemplateFile(row)"
                  >
                    {{ selectedTemplateFile?.id === row.id ? '已选择' : '选择' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!generatorLoading && templateFiles.length === 0" description="暂无模板文件" :image-size="80">
              <el-button type="primary" size="small" @click="uploadDialogVisible = true">去上传</el-button>
            </el-empty>
          </div>
        </div>

        <!-- Step 1: 分析模板 -->
        <div v-else-if="generatorStep === 1" class="step-fade-in">
          <div v-if="!selectedTemplateFile" class="empty-state-small">
            <el-alert type="warning" title="请先返回上一步选择模板文件" show-icon :closable="false" />
          </div>
          <div v-else class="analysis-container">
            <div class="analysis-header">
              <div class="file-info-card">
                <div class="file-icon-wrapper icon-template">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="file-details">
                  <div class="file-name">{{ selectedTemplateFile.filename }}</div>
                  <div class="file-meta">准备进行结构分析</div>
                </div>
              </div>
              <el-button type="primary" :loading="analyzing" @click="handleAnalyzeTemplate" class="analyze-btn">
                <el-icon><DataAnalysis /></el-icon>
                开始分析
              </el-button>
            </div>
            
            <div class="analysis-result" v-if="templateStructure">
              <div class="result-label">模板结构预览</div>
              <div class="code-block">
                <pre>{{ JSON.stringify(templateStructure, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: 选择数据 -->
        <div v-else-if="generatorStep === 2" class="step-fade-in">
          <div class="step-header">
            <div class="info-tag data">
              <el-icon><Folder /></el-icon>
              <span>请选择数据文件</span>
            </div>
            <el-button size="small" circle @click="fetchDataFiles">
              <el-icon><Files /></el-icon>
            </el-button>
          </div>

          <el-alert v-if="selectedDataFile" type="success" :closable="false" class="selection-alert">
            <template #title>
              <div class="selected-info">
                <el-icon><Check /></el-icon>
                <span>已选择: <strong>{{ selectedDataFile.filename }}</strong></span>
              </div>
            </template>
          </el-alert>
          
          <div class="dialog-table-container">
            <el-table 
              :data="dataFiles" 
              height="300" 
              style="width:100%" 
              v-loading="generatorLoading"
              class="custom-table"
              :header-cell-style="{ background: 'transparent' }"
              :row-class-name="getDataRowClass"
            >
              <el-table-column prop="filename" label="数据文件" min-width="240">
                <template #default="{ row }">
                  <div class="filename-cell">
                    <div class="file-icon-wrapper icon-data" style="width: 28px; height: 28px; font-size: 14px;">
                      <el-icon><Folder /></el-icon>
                    </div>
                    <span>{{ row.filename }}</span>
                    <el-tag v-if="selectedDataFile?.id === row.id" type="success" size="small" effect="dark" style="margin-left: auto">已选</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="大小" width="100">
                <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button 
                    :type="selectedDataFile?.id === row.id ? 'success' : 'primary'" 
                    size="small" 
                    link
                    @click="selectDataFile(row)"
                  >
                    {{ selectedDataFile?.id === row.id ? '已选择' : '选择' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!generatorLoading && dataFiles.length === 0" description="暂无数据文件" :image-size="80">
              <el-button type="primary" size="small" @click="uploadDialogVisible = true">去上传</el-button>
            </el-empty>
          </div>
        </div>

        <!-- Step 3: 生成报告 -->
        <div v-else class="step-fade-in">
          <div class="config-card">
            <div class="card-header">生成配置</div>
            <el-form label-width="100px" :model="generateParams" class="config-form">
              <el-form-item label="报告标题">
                <el-input v-model="generateParams.title" placeholder="请输入报告标题（可选）" />
              </el-form-item>
              <el-form-item label="AI 模型">
                <el-select v-model="generateParams.ai_model" style="width: 100%">
                  <el-option label="DeepSeek Chat" value="deepseek-chat" />
                </el-select>
              </el-form-item>
              <el-form-item label="随机性">
                <div style="display: flex; align-items: center; width: 100%; gap: 12px;">
                  <el-slider v-model="generateParams.temperature" :min="0" :max="1" :step="0.1" style="flex: 1" />
                  <span style="font-size: 12px; color: var(--text-tertiary)">{{ generateParams.temperature }}</span>
                </div>
              </el-form-item>
            </el-form>
            
            <div class="summary-box">
              <div class="summary-item">
                <span class="label">模板文件:</span>
                <span class="value">{{ selectedTemplateFile?.filename }}</span>
              </div>
              <div class="summary-item">
                <span class="label">数据文件:</span>
                <span class="value">{{ selectedDataFile?.filename }}</span>
              </div>
            </div>

            <div class="generate-action">
              <el-button 
                type="success" 
                size="large" 
                :disabled="!canStartGenerate" 
                :loading="generating" 
                @click="startGenerate"
                class="generate-btn"
              >
                <el-icon class="el-icon--left"><MagicStick /></el-icon>
                {{ generating ? '正在生成...' : '开始生成报告' }}
              </el-button>
            </div>
          </div>

          <div v-if="currentReport" class="report-preview-card">
             <div class="status-header">
               <span class="status-label">生成状态</span>
               <el-tag :type="currentReportStatus?.status === 'completed' ? 'success' : 'primary'">
                 {{ currentReportStatus?.status || 'Pending' }}
               </el-tag>
             </div>
             <el-progress 
               :percentage="currentReportStatus?.progress || 0" 
               :status="currentReportStatus?.status === 'completed' ? 'success' : ''" 
               :stroke-width="10"
               striped
               striped-flow
             />
             <div v-if="currentReportStatus?.status === 'completed'" class="report-result-box">
                <pre>{{ currentReport.full_text }}</pre>
             </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button v-if="generatorStep > 0" @click="prevStep">上一步</el-button>
          <el-button v-if="generatorStep < 3" type="primary" @click="nextStep">下一步</el-button>
          <el-button v-else @click="generatorDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择模板进入编辑器对话框 -->
    <el-dialog 
      v-model="editorDialogVisible" 
      title="选择模板开始撰写" 
      width="700px" 
      align-center
      class="generator-dialog"
    >
      <div class="generator-content">
        <div class="step-header">
          <div class="info-tag template">
            <el-icon><Document /></el-icon>
            <span>请选择报告模板</span>
          </div>
          <el-button size="small" circle @click="fetchEditorTemplates">
            <el-icon><Files /></el-icon>
          </el-button>
        </div>
        
        <el-alert v-if="selectedEditorTemplate" type="success" :closable="false" class="selection-alert">
          <template #title>
            <div class="selected-info">
              <el-icon><Check /></el-icon>
              <span>已选择: <strong>{{ selectedEditorTemplate.name }}</strong></span>
            </div>
          </template>
        </el-alert>

        <div class="dialog-table-container">
          <el-table 
            :data="editorTemplates" 
            height="350" 
            style="width:100%" 
            v-loading="editorTemplatesLoading"
            class="custom-table"
            :header-cell-style="{ background: 'transparent' }"
          >
            <el-table-column prop="name" label="模板名称" min-width="240">
              <template #default="{ row }">
                <div class="filename-cell">
                  <div class="file-icon-wrapper icon-template" style="width: 28px; height: 28px; font-size: 14px;">
                    <el-icon><Document /></el-icon>
                  </div>
                  <span>{{ row.name }}</span>
                  <el-tag v-if="selectedEditorTemplate?.id === row.id" type="success" size="small" effect="dark" style="margin-left: auto">已选</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'COMPLETED' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button 
                  :type="selectedEditorTemplate?.id === row.id ? 'success' : 'primary'" 
                  size="small" 
                  @click="goToEditor(row)"
                >
                  进入编辑器
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!editorTemplatesLoading && editorTemplates.length === 0" description="暂无已分析的模板" :image-size="80">
            <el-button type="primary" size="small" @click="generatorDialogVisible = true; editorDialogVisible = false">去分析模板</el-button>
          </el-empty>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editorDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useFileStore } from '@/stores/file'
import { formatFileSize, formatDateTime } from '@/utils/format'
import type { FileType, FileInfo } from '@/types'
import type { UploadInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { analyzeTemplate, createTemplate, getTemplates } from '@/api/templates'
import { getAppConfig } from '@/api/config'
import { generateReport, getReportStatus, getReport, getReports, deleteReport } from '@/api/reports'
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
  Check,
  MagicStick,
  Edit
} from '@element-plus/icons-vue'
const CloudUpload = Cloudy

const userStore = useUserStore()
const fileStore = useFileStore()
const disableAIGeneration = ref(false)
const router = useRouter()

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

const reportCount = ref(0)
const statItems = computed(() => [
  { label: '总文件数', value: fileStore.statistics.total_files.toString(), icon: Files },
  { label: '报告模板', value: fileStore.statistics.total_templates.toString(), icon: Document },
  { label: '数据文件', value: fileStore.statistics.total_data_files.toString(), icon: Folder },
  { label: '已生成报告', value: reportCount.value.toString(), icon: DataAnalysis },
])

onMounted(async () => {
  statsLoading.value = true
  await fileStore.fetchFiles()
  await fileStore.fetchStatistics()
  try {
    const reports = await getReports()
    reportCount.value = reports.length
  } catch {}
  try {
    const cfg = await getAppConfig()
    disableAIGeneration.value = !!cfg.featureFlags?.disableAIGeneration
  } catch {}
  statsLoading.value = false
})

const handleFilterChange = async () => {
  currentPage.value = 1
  await fileStore.fetchFiles((filterType.value || undefined) as FileType | undefined)
}

const inferFileType = (name: string): FileType => {
  const lower = name.toLowerCase()
  if (lower.endsWith('.json') || lower.endsWith('.txt')) return 'template'
  if (lower.endsWith('.csv') || lower.endsWith('.xlsx')) return FileType.DATA
  return FileType.OTHER
}

const handleUpload = async (options: any) => {
  const { file } = options
  try {
    uploading.value = true
    const fileType = inferFileType(file.name)
    if (userStore.uploadToOss) {
      await fileStore.uploadFileToOSS(file, fileType)
    } else {
      await fileStore.uploadFile(file, fileType)
    }
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleExceed = (files: File[]) => {
  uploadRef.value!.clearFiles()
  const file = files[0]
  uploadRef.value!.handleStart(file)
}

const handleFileChange = (file: any) => {
  // 可以在这里添加文件校验逻辑
}

const submitUpload = () => {
  uploadRef.value!.submit()
}

// Generator Logic
const generatorDialogVisible = ref(false)
const generatorStep = ref(0)
const generatorLoading = ref(false)
const templateFiles = ref<FileInfo[]>([])
const dataFiles = ref<FileInfo[]>([])
const selectedTemplateFile = ref<FileInfo | null>(null)
const selectedDataFile = ref<FileInfo | null>(null)
const analyzing = ref(false)
const templateStructure = ref<any>(null)
const generating = ref(false)
const currentReport = ref<any>(null)
const currentReportStatus = ref<any>(null)
const selectedTemplateId = ref<number | null>(null)
const currentTemplate = ref<any>(null)

// Editor Entry Logic
const editorDialogVisible = ref(false)
const editorTemplates = ref<any[]>([])
const editorTemplatesLoading = ref(false)
const selectedEditorTemplate = ref<any>(null)

const fetchEditorTemplates = async () => {
  editorTemplatesLoading.value = true
  try {
    const list = await getTemplates()
    // 去重逻辑：按名称分组，取最新的（ID最大的）
    const map = new Map()
    list.forEach((t: any) => {
      if (!map.has(t.name) || t.id > map.get(t.name).id) {
        map.set(t.name, t)
      }
    })
    editorTemplates.value = Array.from(map.values()).sort((a, b) => b.id - a.id)
  } catch (e) {
    ElMessage.error('获取模板列表失败')
  } finally {
    editorTemplatesLoading.value = false
  }
}

const goToEditor = (template: any) => {
  const status = (template.status || '').toUpperCase()
  if (status !== 'COMPLETED' && status !== 'PENDING') {
    ElMessage.warning('该模板尚未分析完成，可能无法正常加载')
  }
  console.log('Navigating to editor for template:', template.id)
  router.push(`/editor/${template.id}`)
  editorDialogVisible.value = false
}

// 监听编辑器对话框打开
watch(editorDialogVisible, (val) => {
  if (val) {
    fetchEditorTemplates()
    selectedEditorTemplate.value = null
  }
})

const reportsDialogVisible = ref(false)
const reportsLoading = ref(false)
const reports = ref<any[]>([])
const reportFilterStatus = ref<'all'|'completed'|'generating'|'failed'>('all')
const filteredReports = computed(() => {
  if (reportFilterStatus.value === 'all') return reports.value
  return reports.value.filter((r: any) => r.status === reportFilterStatus.value)
})
const statusTimers: Record<number, any> = {}
const openReportsDialog = async () => { reportsDialogVisible.value = true; await fetchReports() }
const fetchReports = async () => {
  reportsLoading.value = true
  try {
    const list = await getReports()
    reports.value = list
    list.forEach((r: any) => { if (r.status === 'generating') startPoll(r.id) })
  } finally { reportsLoading.value = false }
}
const viewReport = async (row: any) => {
  const full = await getReport(row.id)
  currentReport.value = full
  currentReportStatus.value = { status: full.status, progress: full.progress }
}
const deleteReportRow = async (row: any) => {
  await deleteReport(row.id)
  await fetchReports()
}
const downloadReportRow = async (row: any) => {
  const full = await getReport(row.id)
  const blob = new Blob([full.full_text || ''], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = (full.title || '报告') + '.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
const startPoll = (id: number) => {
  if (statusTimers[id]) return
  statusTimers[id] = setInterval(async () => {
    const s = await getReportStatus(id)
    const i = reports.value.findIndex((r: any) => r.id === id)
    if (i >= 0) reports.value[i] = { ...reports.value[i], status: (s as any).status, progress: (s as any).progress }
    if ((s as any).status === 'completed' || (s as any).status === 'failed') { clearInterval(statusTimers[id]); delete statusTimers[id] }
  }, 2000)
}
const stopAllPolls = () => { Object.values(statusTimers).forEach((t) => clearInterval(t)); Object.keys(statusTimers).forEach((k) => delete statusTimers[+k]) }

const generateParams = reactive({
  title: '',
  ai_model: 'deepseek-chat',
  temperature: 0.7
})

const canStartGenerate = computed(() => {
  return selectedTemplateId.value && selectedDataFile.value
})

const fetchTemplateFiles = async () => {
  generatorLoading.value = true
  try {
    // 实际应该调用后端筛选接口，这里简单演示
    if (fileStore.files.length === 0) await fileStore.fetchFiles()
    templateFiles.value = fileStore.files.filter(f => f.file_type === 'template' || f.filename.endsWith('.json') || f.filename.endsWith('.txt')) // 简单模拟
  } finally {
    generatorLoading.value = false
  }
}

const fetchDataFiles = async () => {
  generatorLoading.value = true
  try {
    if (fileStore.files.length === 0) await fileStore.fetchFiles()
    dataFiles.value = fileStore.files.filter(f => f.file_type === 'data' || f.filename.endsWith('.csv') || f.filename.endsWith('.xlsx'))
  } finally {
    generatorLoading.value = false
  }
}

// 监听对话框打开，加载初始数据
watch(generatorDialogVisible, (val) => {
  if (val) {
    fetchTemplateFiles()
    fetchDataFiles()
    if (!selectedTemplateFile.value) generatorStep.value = 0
  }
})

const selectTemplateFile = (file: FileInfo) => {
  selectedTemplateFile.value = file
  // 自动下一步
  setTimeout(() => {
    if (generatorStep.value === 0) nextStep()
  }, 300)
}

const selectDataFile = (file: FileInfo) => {
  selectedDataFile.value = file
  setTimeout(() => {
    if (generatorStep.value === 2) nextStep()
  }, 300)
}

const getTemplateRowClass = ({ row }: { row: FileInfo }) => {
  return 'table-row-animate ' + (selectedTemplateFile.value?.id === row.id ? 'selected-row' : '')
}

const getDataRowClass = ({ row }: { row: FileInfo }) => {
  return 'table-row-animate ' + (selectedDataFile.value?.id === row.id ? 'selected-row' : '')
}

const handleAnalyzeTemplate = async () => {
  if (!selectedTemplateFile.value) return
  analyzing.value = true
  try {
    if (!selectedTemplateId.value) {
      const created = await createTemplate({
        name: selectedTemplateFile.value.filename,
        description: '由文件自动创建',
        file_id: (selectedTemplateFile.value as any).id,
      } as any)
      currentTemplate.value = created
      selectedTemplateId.value = (created as any).id
    }
    const analyzed = await analyzeTemplate(selectedTemplateId.value as number)
    templateStructure.value = (analyzed as any).structure || analyzed
    ElMessage.success('模板分析完成')
    router.push(`/editor/${selectedTemplateId.value}`)
  } catch (e: any) {
    ElMessage.error('模板分析失败')
  } finally {
    analyzing.value = false
  }
}

const startGenerate = async () => {
  if (!selectedTemplateId.value || !selectedDataFile.value) return
  generating.value = true
  try {
    const created = await generateReport({
      template_id: selectedTemplateId.value as number,
      data_file_id: selectedDataFile.value.id,
      title: generateParams.title,
      ai_model: generateParams.ai_model,
      temperature: generateParams.temperature,
    } as any)
    currentReport.value = created
    const timer = setInterval(async () => {
      const status = await getReportStatus((created as any).id)
      currentReportStatus.value = status as any
      if ((status as any).status === 'completed' || (status as any).status === 'failed') {
        clearInterval(timer)
        if ((status as any).status === 'completed') {
          const full = await getReport((created as any).id)
          currentReport.value = full
        }
      }
    }, 1500)
  } finally {
    generating.value = false
  }
}

const nextStep = () => { generatorStep.value = Math.min(3, generatorStep.value + 1) }
const prevStep = () => { generatorStep.value = Math.max(0, generatorStep.value - 1) }

const handleLogout = () => {
  userStore.logout()
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

// 主题切换
const isDark = ref(localStorage.getItem('theme') === 'dark')

watch(isDark, (val) => {
  document.documentElement.classList.toggle('dark', val)
  localStorage.setItem('theme', val ? 'dark' : 'light')
}, { immediate: true })
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
  top: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: var(--brand-primary);
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
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, var(--text-primary), var(--brand-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-24);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: 600;
  color: var(--text-primary);
}

.user-avatar {
  background: var(--brand-primary-light);
  color: white;
  font-weight: 700;
}

.logout-btn {
  margin-left: 8px;
}

.dashboard-main {
  flex: 1;
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

/* 选中行的样式 */
:deep(.selected-row) {
  background: rgba(103, 194, 58, 0.1) !important;
  border-left: 3px solid #67c23a;
  transition: all 0.3s ease;
}

:deep(.selected-row:hover) {
  background: rgba(103, 194, 58, 0.15) !important;
  transform: scale(1.01);
}

:root.dark :deep(.selected-row) {
  background: rgba(103, 194, 58, 0.15) !important;
}

:root.dark :deep(.selected-row:hover) {
  background: rgba(103, 194, 58, 0.2) !important;
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

/* Generator Dialog Styles */
.generator-content {
  min-height: 400px;
  padding: 20px 0;
}

.step-fade-in {
  animation: fadeIn 0.4s ease-out;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.info-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

:root.dark .info-tag {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: var(--glass-border);
  box-shadow: var(--shadow-sm);
}

.info-tag.template { color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
.info-tag.data { color: #10b981; background: rgba(16, 185, 129, 0.1); }

:root.dark .info-tag.template {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

:root.dark .info-tag.data {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.selection-alert {
  margin-bottom: 16px;
  border: 1px solid rgba(103, 194, 58, 0.2);
  background: rgba(103, 194, 58, 0.1);
}

:root.dark .selection-alert {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  backdrop-filter: blur(12px);
}

.selected-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.dialog-table-container {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
}

:root.dark .dialog-table-container {
  background: rgba(0, 0, 0, 0.2);
}

.empty-state-small {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

/* Analysis Step */
.analysis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

:root.dark .analysis-header {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: var(--glass-border);
}

.file-info-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.file-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.analyze-btn {
  padding: 10px 24px;
  font-weight: 600;
}

.analysis-result {
  background: #1e1e1e;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid #333;
}

.result-label {
  padding: 8px 16px;
  background: #2d2d2d;
  color: #aaa;
  font-size: 12px;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.code-block {
  padding: 16px;
  max-height: 300px;
  overflow: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  color: #d4d4d4;
  line-height: 1.5;
}

/* Config Step */
.config-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid var(--border-color);
  margin-bottom: 24px;
}

:root.dark .config-card {
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(16px);
  border: var(--glass-border);
  box-shadow: var(--shadow-glass);
}

.card-header {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.config-form {
  max-width: 600px;
}

.summary-box {
  margin-top: 20px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  gap: 24px;
}

:root.dark .summary-box {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(8px);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-item .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.summary-item .value {
  font-weight: 600;
  color: var(--text-primary);
}

.generate-action {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.generate-btn {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(103, 194, 58, 0.3);
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
}

.report-preview-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid var(--border-color);
}

:root.dark .report-preview-card {
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(16px);
  border: var(--glass-border);
  box-shadow: var(--shadow-glass);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-label {
  font-weight: 600;
  color: var(--text-primary);
}

.report-result-box {
  margin-top: 16px;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  max-height: 300px;
  overflow: auto;
}

:root.dark .report-result-box {
  background: rgba(0, 0, 0, 0.3);
  border: var(--glass-border);
  backdrop-filter: blur(8px);
}

.report-result-box pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
}

:root.dark :deep(.el-progress-bar__outer) {
  background-color: rgba(255, 255, 255, 0.05);
}
</style>

<style>
/* Generator Dialog - Global Overrides */
.generator-dialog {
  --el-dialog-bg-color: rgba(255, 255, 255, 0.9);
  border-radius: 16px !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
}

html.dark .generator-dialog {
  --el-dialog-bg-color: rgba(15, 23, 42, 0.85) !important; /* Deep Dark Slate */
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
}

/* Header */
.generator-dialog .el-dialog__header {
  margin-right: 0;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
html.dark .generator-dialog .el-dialog__header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
html.dark .generator-dialog .el-dialog__title {
  color: #f1f5f9;
}

/* Body */
.generator-dialog .el-dialog__body {
  padding: 0 24px 24px;
}

/* Footer */
.generator-dialog .el-dialog__footer {
  padding: 20px 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}
html.dark .generator-dialog .el-dialog__footer {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* Steps */
html.dark .generator-dialog .el-step__title.is-process { color: #38bdf8; font-weight: 600; }
html.dark .generator-dialog .el-step__title.is-wait { color: #64748b; }
html.dark .generator-dialog .el-step__title.is-success { color: #4ade80; }

/* Table Transparency */
html.dark .generator-dialog .el-table,
html.dark .generator-dialog .el-table__expanded-cell {
  background-color: transparent !important;
  --el-table-bg-color: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: rgba(255, 255, 255, 0.02) !important;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.05) !important;
  color: #e2e8f0;
}

html.dark .generator-dialog .el-table th,
html.dark .generator-dialog .el-table tr,
html.dark .generator-dialog .el-table td {
  background-color: transparent !important;
  border-bottom-color: rgba(255, 255, 255, 0.05) !important;
}

/* Inputs & Form Items */
html.dark .generator-dialog .el-form-item__label {
  color: #cbd5e1;
}
html.dark .generator-dialog .el-input__wrapper,
html.dark .generator-dialog .el-textarea__wrapper,
html.dark .generator-dialog .el-select__wrapper {
  background-color: rgba(15, 23, 42, 0.5);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}
html.dark .generator-dialog .el-input__inner {
  color: #f8fafc;
}

/* Buttons in Dialog */
html.dark .generator-dialog .el-button--default {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}
html.dark .generator-dialog .el-button--default:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}
</style>
