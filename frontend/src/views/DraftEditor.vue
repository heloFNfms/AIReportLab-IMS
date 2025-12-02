<template>
  <div class="draft-editor">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="handleExit" type="default">
          <el-icon><ArrowLeft /></el-icon>
          <span>退出</span>
        </el-button>
        <el-divider direction="vertical" />
        <div class="draft-info">
          <h3>{{ currentDraft?.title || '加载中...' }}</h3>
          <div class="meta-info">
            <el-tag :type="currentDraft?.status === 'draft' ? 'success' : 'primary'" size="small">
              {{ currentDraft?.status === 'draft' ? '草稿' : '已完成' }}
            </el-tag>
            <span>v{{ currentDraft?.current_version }}</span>
            <span>{{ wordCount }}字</span>
            <span class="save-status" :class="saveStatusClass">
              <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
              <el-icon v-else-if="saveStatus === 'saved'"><CircleCheck /></el-icon>
              <el-icon v-else-if="saveStatus === 'error'"><CircleClose /></el-icon>
              <el-icon v-else-if="hasUnsavedChanges"><Warning /></el-icon>
              {{ saveStatusText }}
            </span>
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
        <el-button @click="handleManualSave" :loading="saving" type="primary" size="small">
          <el-icon><Document /></el-icon> 保存
        </el-button>
        <el-dropdown @command="handleExport" trigger="click">
          <el-button size="small" type="success">
            <el-icon><Download /></el-icon> 导出<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="markdown">Markdown (.md)</el-dropdown-item>
              <el-dropdown-item command="html">HTML 网页</el-dropdown-item>
              <el-dropdown-item command="word">Word (.docx)</el-dropdown-item>
              <el-dropdown-item command="pdf" divided>打印/PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-dropdown @command="handleCommand">
          <el-button size="small">更多<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="complete" v-if="currentDraft?.status === 'draft'">完成报告</el-dropdown-item>
              <el-dropdown-item command="reopen" v-if="currentDraft?.status === 'completed'">重新编辑</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除草稿</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <div class="editor-main" :class="{ 'with-data-panel': showDataPanel }">
      <div class="editor-panel">
        <MarkdownEditor ref="markdownEditorRef" v-model="editorContent" :height="editorHeight" mode="ir" placeholder="开始撰写..." @change="handleContentChange" />
      </div>
      <div v-if="showDataPanel" class="data-panel">
        <div class="data-panel-header">
          <h4>数据预览</h4>
          <el-button size="small" type="primary" @click="showFileSelector = true"><el-icon><FolderOpened /></el-icon></el-button>
        </div>
        <div class="data-panel-content">
          <div v-if="!selectedDataFile" class="no-file-selected">
            <el-empty description="未选择文件" :image-size="60"><el-button size="small" @click="showFileSelector = true">选择</el-button></el-empty>
          </div>
          <div v-else class="file-preview">
            <div class="file-info-bar">
              <span class="file-name"><el-icon><Document /></el-icon>{{ selectedDataFile.filename }}</span>
              <span><el-button size="small" text @click="copyDataToEditor"><el-icon><CopyDocument /></el-icon></el-button>
              <el-button size="small" text type="danger" @click="clearDataFile"><el-icon><Close /></el-icon></el-button></span>
            </div>
            <div v-if="previewLoading" class="preview-loading"><el-skeleton :rows="8" animated /></div>
            <div v-else-if="!previewData?.preview_available" class="preview-error"><el-alert :title="previewData?.message" type="warning" :closable="false" /></div>
            <div v-else class="preview-content"><pre>{{ previewData.content }}</pre></div>
          </div>
        </div>
      </div>
    </div>
    <el-dialog v-model="showVersionHistory" title="版本历史" width="600px">
      <div class="version-list">
        <div v-for="v in versions" :key="v.id" class="version-item" :class="{ current: v.version === currentDraft?.current_version }">
          <div class="version-header"><strong>版本 {{ v.version }}</strong><span>{{ formatDate(v.created_at) }}</span></div>
          <div class="version-summary">{{ v.change_summary || '无说明' }} · {{ v.word_count }}字</div>
          <el-button v-if="v.version !== currentDraft?.current_version" @click="rollbackToVersion(v.version)" size="small">回滚</el-button>
        </div>
      </div>
    </el-dialog>
    <el-dialog v-model="showFileSelector" title="选择数据文件" width="500px">
      <div v-if="dataFilesLoading"><el-skeleton :rows="4" animated /></div>
      <div v-else-if="dataFiles.length === 0"><el-empty description="暂无数据文件" /></div>
      <div v-else class="file-list">
        <div v-for="f in dataFiles" :key="f.id" class="file-item" :class="{ selected: tempSelectedFile?.id === f.id }" @click="tempSelectedFile = f">
          <el-icon><Document /></el-icon>
          <div class="file-details"><div>{{ f.filename }}</div><small>{{ formatFileSize(f.file_size) }}</small></div>
          <el-icon v-if="tempSelectedFile?.id === f.id" class="check"><Check /></el-icon>
        </div>
      </div>
      <template #footer><el-button @click="showFileSelector = false">取消</el-button><el-button type="primary" @click="confirmFileSelection" :disabled="!tempSelectedFile">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Clock, Document, ArrowDown, View, FolderOpened, Close, Check, Download, Loading, CircleCheck, CircleClose, Warning, CopyDocument } from '@element-plus/icons-vue'
import { useDraftStore } from '@/stores/draft'
import { useFileStore } from '@/stores/file'
import { previewFile, type FilePreview } from '@/api/files'
import { formatDate, formatFileSize } from '@/utils/format'
import { exportReport, type ExportFormat } from '@/utils/export'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import type { DraftVersion, FileInfo } from '@/types'

const route = useRoute()
const router = useRouter()
const draftStore = useDraftStore()
const fileStore = useFileStore()

const draftId = parseInt(route.params.id as string)
const currentDraft = ref(draftStore.currentDraft)
const versions = ref<DraftVersion[]>([])
const editorContent = ref('')
const originalContent = ref('')
const showVersionHistory = ref(false)
const saving = ref(false)
const saveStatus = ref<'idle' | 'saved' | 'error'>('idle')
const lastSaveTime = ref<Date | null>(null)
const markdownEditorRef = ref<InstanceType<typeof MarkdownEditor>>()

const hasUnsavedChanges = computed(() => editorContent.value !== originalContent.value)
const saveStatusClass = computed(() => ({ 'status-saving': saving.value, 'status-saved': saveStatus.value === 'saved', 'status-error': saveStatus.value === 'error', 'status-unsaved': hasUnsavedChanges.value && saveStatus.value === 'idle' }))
const saveStatusText = computed(() => {
  if (saving.value) return '保存中...'
  if (saveStatus.value === 'saved') return '已保存'
  if (saveStatus.value === 'error') return '保存失败'
  if (hasUnsavedChanges.value) return '未保存'
  return ''
})
const wordCount = computed(() => {
  if (!editorContent.value) return 0
  return (editorContent.value.match(/[\u4e00-\u9fff]/g) || []).length + (editorContent.value.match(/[a-zA-Z]+/g) || []).length
})
const editorHeight = computed(() => 'calc(100vh - 140px)')

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
    originalContent.value = draft.content || ''
    if (draft.data_file_id) {
      await loadDataFiles()
      const file = dataFiles.value.find(f => f.id === draft.data_file_id)
      if (file) { selectedDataFile.value = file; showDataPanel.value = true; await loadFilePreview(file.id) }
    }
  } catch { ElMessage.error('加载失败'); router.push('/') }
}

const loadDataFiles = async () => {
  dataFilesLoading.value = true
  try { await fileStore.fetchFiles(); dataFiles.value = fileStore.files.filter(f => String(f.file_type).toUpperCase() === 'DATA') }
  finally { dataFilesLoading.value = false }
}

const loadFilePreview = async (fileId: number) => {
  previewLoading.value = true
  try { previewData.value = await previewFile(fileId) }
  catch { previewData.value = { file_id: fileId, filename: '', preview_available: false, content: null, message: '加载失败' } }
  finally { previewLoading.value = false }
}

const toggleDataPanel = async () => { showDataPanel.value = !showDataPanel.value; if (showDataPanel.value && !dataFiles.value.length) await loadDataFiles() }
const confirmFileSelection = async () => {
  if (!tempSelectedFile.value) return
  selectedDataFile.value = tempSelectedFile.value
  showFileSelector.value = false
  if (currentDraft.value) await draftStore.updateDraft(currentDraft.value.id, { data_file_id: tempSelectedFile.value.id })
  await loadFilePreview(tempSelectedFile.value.id)
  tempSelectedFile.value = null
}
const clearDataFile = async () => { selectedDataFile.value = null; previewData.value = null; if (currentDraft.value) await draftStore.updateDraft(currentDraft.value.id, { data_file_id: undefined }) }
const copyDataToEditor = () => { if (previewData.value?.content && markdownEditorRef.value) { markdownEditorRef.value.insertValue(`\n\`\`\`\n${previewData.value.content}\n\`\`\`\n`); ElMessage.success('已插入') } }

const handleContentChange = () => { saveStatus.value = 'idle'; if (autoSaveTimer) clearTimeout(autoSaveTimer); autoSaveTimer = setTimeout(() => saveDraft(true), 5000) }

const saveDraft = async (isAutoSave = false): Promise<boolean> => {
  if (!currentDraft.value || saving.value) return false
  if (isAutoSave && !hasUnsavedChanges.value) return true
  try {
    saving.value = true
    await draftStore.updateDraft(currentDraft.value.id, { content: editorContent.value, change_summary: isAutoSave ? '自动保存' : '手动保存' })
    originalContent.value = editorContent.value
    saveStatus.value = 'saved'
    lastSaveTime.value = new Date()
    if (!isAutoSave) ElMessage.success('保存成功')
    return true
  } catch { 
    saveStatus.value = 'error'
    if (!isAutoSave) ElMessage.error('保存失败')
    return false
  } finally { 
    saving.value = false 
  }
}

const handleManualSave = () => saveDraft(false)

const handleExit = async () => {
  if (hasUnsavedChanges.value) {
    try {
      await ElMessageBox.confirm('有未保存的更改，是否保存？', '提示', { 
        distinguishCancelAndClose: true, 
        confirmButtonText: '保存并退出', 
        cancelButtonText: '不保存', 
        type: 'warning' 
      })
      // 用户点击"保存并退出"
      const success = await saveDraft(false)
      if (success) {
        router.push('/template-select')
      }
    } catch (action) { 
      // 用户点击"不保存" (cancel) 或 关闭弹窗 (close)
      if (action === 'cancel') {
        router.push('/template-select') 
      }
      // action === 'close' 时不做任何操作，留在当前页面
    }
  } else { 
    router.push('/template-select') 
  }
}

const handleExport = async (format: ExportFormat) => {
  if (!currentDraft.value) return
  ElMessage.info('正在导出...')
  const success = await exportReport(format, editorContent.value, markdownEditorRef.value?.getHTML() || editorContent.value, currentDraft.value.title, currentDraft.value.title.replace(/[\\/:*?"<>|]/g, '_'))
  if (success && format !== 'pdf') ElMessage.success('导出成功')
}

const handleCommand = async (cmd: string) => {
  if (!currentDraft.value) return
  if (cmd === 'complete') { await ElMessageBox.confirm('确定完成？', '确认'); await draftStore.completeDraft(currentDraft.value.id, { content: editorContent.value }); originalContent.value = editorContent.value; await loadDraft(); ElMessage.success('已完成') }
  else if (cmd === 'reopen') { await draftStore.reopenDraft(currentDraft.value.id); await loadDraft() }
  else if (cmd === 'delete') { await ElMessageBox.confirm('确定删除？', '确认', { type: 'warning' }); await draftStore.deleteDraft(currentDraft.value.id); router.push('/draft-box') }
}

const rollbackToVersion = async (version: number) => {
  if (!currentDraft.value) return
  await ElMessageBox.confirm(`回滚到版本 ${version}？`, '确认')
  await draftStore.rollbackVersion(currentDraft.value.id, version)
  await loadDraft()
  showVersionHistory.value = false
  ElMessage.success('已回滚')
}

const handleBeforeUnload = (e: BeforeUnloadEvent) => { if (hasUnsavedChanges.value) { e.preventDefault(); e.returnValue = '' } }
const handleKeydown = (e: KeyboardEvent) => { if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); handleManualSave() } }

onMounted(() => { loadDraft(); window.addEventListener('beforeunload', handleBeforeUnload); window.addEventListener('keydown', handleKeydown) })
onBeforeUnmount(() => { if (autoSaveTimer) clearTimeout(autoSaveTimer); window.removeEventListener('beforeunload', handleBeforeUnload); window.removeEventListener('keydown', handleKeydown) })
</script>


<style scoped>
.draft-editor { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; overflow: hidden; }
.editor-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: white; border-bottom: 1px solid #e4e7ed; flex-shrink: 0; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left .el-divider { height: 24px; }
.draft-info h3 { margin: 0 0 2px 0; color: #303133; font-size: 15px; font-weight: 600; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta-info { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #909399; }
.header-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.save-status { display: flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.save-status.status-saving { color: #409eff; }
.save-status.status-saved { color: #67c23a; background: #f0f9eb; }
.save-status.status-error { color: #f56c6c; background: #fef0f0; }
.save-status.status-unsaved { color: #e6a23c; background: #fdf6ec; }

.editor-main { flex: 1; display: flex; gap: 16px; padding: 16px; overflow: hidden; }
.editor-panel { flex: 1; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }

.data-panel { width: 380px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
.data-panel-header { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #e4e7ed; background: #fafafa; }
.data-panel-header h4 { margin: 0; font-size: 14px; }
.data-panel-content { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.no-file-selected { flex: 1; display: flex; align-items: center; justify-content: center; }
.file-preview { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.file-info-bar { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f0f9ff; border-bottom: 1px solid #e4e7ed; }
.file-info-bar .file-name { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #409eff; }
.preview-loading, .preview-error { padding: 16px; }
.preview-content { flex: 1; overflow: auto; padding: 12px; background: #fafafa; }
.preview-content pre { margin: 0; font-family: monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; }

.version-list { max-height: 400px; overflow-y: auto; }
.version-item { padding: 12px; border-bottom: 1px solid #eee; }
.version-item.current { background: #f0f9ff; border-left: 3px solid #409eff; }
.version-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.version-summary { color: #666; font-size: 13px; margin-bottom: 8px; }

.file-list { max-height: 300px; overflow-y: auto; }
.file-item { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 6px; cursor: pointer; border: 2px solid transparent; }
.file-item:hover { background: #f5f7fa; }
.file-item.selected { background: #ecf5ff; border-color: #409eff; }
.file-details { flex: 1; }
.file-details small { color: #909399; }
.check { color: #67c23a; }
</style>
