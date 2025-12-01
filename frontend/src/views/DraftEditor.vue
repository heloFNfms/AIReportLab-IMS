<template>
  <div class="draft-editor">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="goBack" size="small">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <div class="draft-info">
          <h3>{{ currentDraft?.title || '加载中...' }}</h3>
          <div class="meta-info">
            <span class="status-badge" :class="currentDraft?.status">
              {{ currentDraft?.status === 'draft' ? '草稿' : '已完成' }}
            </span>
            <span>版本 {{ currentDraft?.current_version }}</span>
            <span>{{ currentDraft?.word_count }} 字</span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="toggleDataPanel" :type="showDataPanel ? 'primary' : 'default'" size="small">
          <el-icon><View /></el-icon> {{ showDataPanel ? '隐藏数据' : '查看数据' }}
        </el-button>
        <el-button @click="showVersionHistory = true" size="small">
          <el-icon><Clock /></el-icon> 版本历史
        </el-button>
        <el-button @click="saveDraft" :loading="saving" type="primary" size="small">
          <el-icon><Document /></el-icon> 保存
        </el-button>
        <el-dropdown @command="handleCommand">
          <el-button size="small">更多<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="complete" v-if="currentDraft?.status === 'draft'">完成报告</el-dropdown-item>
              <el-dropdown-item command="reopen" v-if="currentDraft?.status === 'completed'">重新编辑</el-dropdown-item>
              <el-dropdown-item command="export">导出文档</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除草稿</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="editor-main" :class="{ 'with-data-panel': showDataPanel }">
      <!-- 左侧编辑区 -->
      <div class="editor-panel">
        <el-input
          v-model="editorContent"
          type="textarea"
          placeholder="开始撰写你的报告..."
          @input="handleContentChange"
          class="content-textarea"
        />
      </div>

      <!-- 右侧数据预览面板 -->
      <div v-if="showDataPanel" class="data-panel">
        <div class="data-panel-header">
          <h4>数据文件预览</h4>
          <el-button size="small" type="primary" @click="showFileSelector = true">
            <el-icon><FolderOpened /></el-icon> 选择文件
          </el-button>
        </div>
        
        <div class="data-panel-content">
          <div v-if="!selectedDataFile" class="no-file-selected">
            <el-empty description="未选择数据文件">
              <el-button type="primary" @click="showFileSelector = true">选择数据文件</el-button>
            </el-empty>
          </div>
          
          <div v-else class="file-preview">
            <div class="file-info-bar">
              <div class="file-name">
                <el-icon><Document /></el-icon>
                <span>{{ selectedDataFile.filename }}</span>
              </div>
              <el-button size="small" text type="danger" @click="clearDataFile">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            
            <div v-if="previewLoading" class="preview-loading">
              <el-skeleton :rows="10" animated />
            </div>
            
            <div v-else-if="!previewData?.preview_available" class="preview-error">
              <el-alert :title="previewData?.message || '无法预览此文件'" type="warning" :closable="false" />
            </div>
            
            <div v-else class="preview-content">
              <pre>{{ previewData.content }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="showVersionHistory" title="版本历史" width="600px">
      <div class="version-list">
        <div v-for="version in versions" :key="version.id" class="version-item">
          <div class="version-header">
            <strong>版本 {{ version.version }}</strong>
            <span>{{ formatDate(version.created_at) }}</span>
          </div>
          <div class="version-summary">{{ version.change_summary || '无变更说明' }}</div>
          <el-button 
            v-if="version.version !== currentDraft?.current_version"
            @click="rollbackToVersion(version.version)" 
            size="small"
          >回滚</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 数据文件选择对话框 -->
    <el-dialog v-model="showFileSelector" title="选择数据文件" width="600px">
      <div v-if="dataFilesLoading" class="files-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="dataFiles.length === 0" class="no-files">
        <el-empty description="暂无数据文件">
          <el-button type="primary" @click="goToUpload">去上传</el-button>
        </el-empty>
      </div>
      <div v-else class="file-list">
        <div 
          v-for="file in dataFiles" 
          :key="file.id" 
          class="file-item"
          :class="{ selected: selectedDataFile?.id === file.id }"
          @click="selectFile(file)"
        >
          <div class="file-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="file-details">
            <div class="file-name">{{ file.filename }}</div>
            <div class="file-meta">{{ formatFileSize(file.file_size) }} · {{ formatDate(file.created_at) }}</div>
          </div>
          <el-icon v-if="selectedDataFile?.id === file.id" class="check-icon"><Check /></el-icon>
        </div>
      </div>
      <template #footer>
        <el-button @click="showFileSelector = false">取消</el-button>
        <el-button type="primary" @click="confirmFileSelection" :disabled="!tempSelectedFile">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Clock, Document, ArrowDown, View, FolderOpened, Close, Check } from '@element-plus/icons-vue'
import { useDraftStore } from '@/stores/draft'
import { useFileStore } from '@/stores/file'
import { previewFile, type FilePreview } from '@/api/files'
import { formatDate, formatFileSize } from '@/utils/format'
import type { DraftVersion, FileInfo } from '@/types'

const route = useRoute()
const router = useRouter()
const draftStore = useDraftStore()
const fileStore = useFileStore()

const draftId = parseInt(route.params.id as string)
const currentDraft = ref(draftStore.currentDraft)
const versions = ref<DraftVersion[]>([])
const editorContent = ref('')
const showVersionHistory = ref(false)
const saving = ref(false)

// 数据面板相关
const showDataPanel = ref(false)
const showFileSelector = ref(false)
const dataFiles = ref<FileInfo[]>([])
const dataFilesLoading = ref(false)
const selectedDataFile = ref<FileInfo | null>(null)
const tempSelectedFile = ref<FileInfo | null>(null)
const previewData = ref<FilePreview | null>(null)
const previewLoading = ref(false)

let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

const loadDraft = async () => {
  try {
    const draft = await draftStore.fetchDraftDetail(draftId)
    currentDraft.value = draft
    versions.value = draft.versions || []
    editorContent.value = draft.content || ''
    
    // 如果草稿关联了数据文件，加载它
    if (draft.data_file_id) {
      await loadDataFiles()
      const file = dataFiles.value.find(f => f.id === draft.data_file_id)
      if (file) {
        selectedDataFile.value = file
        showDataPanel.value = true
        await loadFilePreview(file.id)
      }
    }
  } catch {
    ElMessage.error('加载草稿失败')
    router.push('/')
  }
}

const loadDataFiles = async () => {
  dataFilesLoading.value = true
  try {
    await fileStore.fetchFiles()
    dataFiles.value = fileStore.files.filter(f => String(f.file_type).toUpperCase() === 'DATA')
  } finally {
    dataFilesLoading.value = false
  }
}

const loadFilePreview = async (fileId: number) => {
  previewLoading.value = true
  try {
    previewData.value = await previewFile(fileId)
  } catch (error) {
    previewData.value = {
      file_id: fileId,
      filename: '',
      preview_available: false,
      content: null,
      message: '加载预览失败'
    }
  } finally {
    previewLoading.value = false
  }
}

const toggleDataPanel = async () => {
  showDataPanel.value = !showDataPanel.value
  if (showDataPanel.value && dataFiles.value.length === 0) {
    await loadDataFiles()
  }
}

const selectFile = (file: FileInfo) => {
  tempSelectedFile.value = file
}

const confirmFileSelection = async () => {
  if (!tempSelectedFile.value) return
  
  selectedDataFile.value = tempSelectedFile.value
  showFileSelector.value = false
  
  // 更新草稿的数据文件关联
  if (currentDraft.value) {
    await draftStore.updateDraft(currentDraft.value.id, {
      data_file_id: tempSelectedFile.value.id
    })
  }
  
  // 加载文件预览
  await loadFilePreview(tempSelectedFile.value.id)
  tempSelectedFile.value = null
}

const clearDataFile = async () => {
  selectedDataFile.value = null
  previewData.value = null
  
  // 清除草稿的数据文件关联
  if (currentDraft.value) {
    await draftStore.updateDraft(currentDraft.value.id, {
      data_file_id: undefined
    })
  }
}

const goToUpload = () => {
  showFileSelector.value = false
  router.push('/')
}

const handleContentChange = () => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => saveDraft(true), 3000)
}

const saveDraft = async (isAutoSave = false) => {
  if (!currentDraft.value) return
  try {
    saving.value = true
    await draftStore.updateDraft(currentDraft.value.id, {
      content: editorContent.value,
      change_summary: isAutoSave ? '自动保存' : undefined
    })
    if (!isAutoSave) ElMessage.success('保存成功')
  } catch {
    if (!isAutoSave) ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleCommand = async (command: string) => {
  if (!currentDraft.value) return
  switch (command) {
    case 'complete': await completeDraft(); break
    case 'reopen': await reopenDraft(); break
    case 'export': exportDocument(); break
    case 'delete': await deleteDraft(); break
  }
}

const completeDraft = async () => {
  if (!currentDraft.value) return
  try {
    await ElMessageBox.confirm('确定要完成这个报告吗？', '确认完成')
    await draftStore.completeDraft(currentDraft.value.id, { content: editorContent.value })
    await loadDraft()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const reopenDraft = async () => {
  if (!currentDraft.value) return
  await draftStore.reopenDraft(currentDraft.value.id)
  await loadDraft()
}

const exportDocument = () => {
  if (!currentDraft.value || !editorContent.value) {
    ElMessage.warning('没有内容可导出')
    return
  }
  const blob = new Blob([editorContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentDraft.value.title}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const deleteDraft = async () => {
  if (!currentDraft.value) return
  try {
    await ElMessageBox.confirm('确定要删除这个草稿吗？', '确认删除', { type: 'warning' })
    await draftStore.deleteDraft(currentDraft.value.id)
    router.push('/')
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const rollbackToVersion = async (version: number) => {
  if (!currentDraft.value) return
  try {
    await ElMessageBox.confirm(`确定要回滚到版本 ${version} 吗？`, '确认回滚')
    await draftStore.rollbackVersion(currentDraft.value.id, version)
    await loadDraft()
    showVersionHistory.value = false
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const goBack = () => router.push('/')

watch(() => draftStore.currentDraft, (newDraft) => { currentDraft.value = newDraft })

onMounted(() => loadDraft())
</script>

<style scoped>
.draft-editor { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.editor-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: white; border-bottom: 1px solid #e4e7ed; }
.header-left { display: flex; align-items: center; gap: 16px; }
.draft-info h3 { margin: 0 0 4px 0; color: #303133; font-size: 16px; }
.meta-info { display: flex; align-items: center; gap: 12px; font-size: 12px; color: #909399; }
.status-badge { padding: 2px 8px; border-radius: 12px; font-size: 11px; }
.status-badge.draft { background: #e1f3d8; color: #67c23a; }
.status-badge.completed { background: #d9ecff; color: #409eff; }
.header-right { display: flex; align-items: center; gap: 8px; }

.editor-main { flex: 1; display: flex; gap: 16px; padding: 16px; overflow: hidden; }
.editor-main.with-data-panel .editor-panel { flex: 1; }

.editor-panel { 
  flex: 1; 
  background: white; 
  border-radius: 8px; 
  padding: 16px; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}
.content-textarea { flex: 1; }
.content-textarea :deep(.el-textarea__inner) { 
  height: 100% !important; 
  min-height: 400px;
  resize: none; 
  border: none; 
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; 
  font-size: 14px; 
  line-height: 1.6; 
}

/* 数据预览面板 */
.data-panel {
  width: 420px;
  min-width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.data-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}
.data-panel-header h4 { margin: 0; font-size: 14px; color: #303133; }

.data-panel-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.no-file-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.file-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f0f9ff;
  border-bottom: 1px solid #e4e7ed;
}
.file-info-bar .file-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #409eff;
  font-weight: 500;
}

.preview-loading, .preview-error {
  padding: 16px;
}

.preview-content {
  flex: 1;
  overflow: auto;
  padding: 12px;
  background: #fafafa;
}
.preview-content pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  color: #303133;
}

/* 版本历史 */
.version-list { max-height: 400px; overflow-y: auto; }
.version-item { padding: 12px; border-bottom: 1px solid #e4e7ed; }
.version-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.version-summary { color: #606266; font-size: 14px; margin-bottom: 8px; }

/* 文件选择对话框 */
.files-loading, .no-files { padding: 20px; }
.file-list { max-height: 400px; overflow-y: auto; }
.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}
.file-item:hover { background: #f5f7fa; }
.file-item.selected { 
  background: #ecf5ff; 
  border-color: #409eff;
}
.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #e6f7ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.file-details { flex: 1; }
.file-details .file-name { font-weight: 500; color: #303133; margin-bottom: 4px; }
.file-details .file-meta { font-size: 12px; color: #909399; }
.check-icon { color: #67c23a; font-size: 20px; }
</style>
