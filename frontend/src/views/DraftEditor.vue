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
        <!-- AI 助手下拉菜单 -->
        <!-- 大纲生成按钮 -->
        <el-button @click="showOutlineGenerator = true" type="primary" size="small">
          <el-icon><List /></el-icon> 生成大纲
        </el-button>
        
        <el-dropdown @command="handleAIAction" trigger="click">
          <el-button size="small" type="warning">
            <el-icon><MagicStick /></el-icon> AI助手<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="polish">✨ 润色文本</el-dropdown-item>
              <el-dropdown-item command="expand">📝 扩写内容</el-dropdown-item>
              <el-dropdown-item command="condense">📉 精简内容</el-dropdown-item>
              <el-dropdown-item command="rewrite">🔄 改写表达</el-dropdown-item>
              <el-dropdown-item command="continue" divided>➡️ 续写内容</el-dropdown-item>
              <el-dropdown-item command="explain">💡 解释说明</el-dropdown-item>
              <el-dropdown-item command="translate_en" divided>🇬🇧 翻译英文</el-dropdown-item>
              <el-dropdown-item command="translate_zh">🇨🇳 翻译中文</el-dropdown-item>
              <el-dropdown-item command="ask" divided>💬 AI 问答</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
      <div class="editor-panel" ref="editorPanelRef">
        <MarkdownEditor ref="markdownEditorRef" v-model="editorContent" :height="editorHeight" mode="ir" placeholder="开始撰写..." @change="handleContentChange" @selection="handleTextSelection" />
        
        <!-- 选中文本时的浮动 AI 工具栏 -->
        <transition name="fade">
          <div v-if="showFloatingToolbar && selectedText" class="floating-ai-toolbar" :style="floatingToolbarStyle">
            <el-button-group size="small">
              <el-tooltip content="润色" placement="top">
                <el-button @click="handleFloatingAI('polish')">✨</el-button>
              </el-tooltip>
              <el-tooltip content="扩写" placement="top">
                <el-button @click="handleFloatingAI('expand')">📝</el-button>
              </el-tooltip>
              <el-tooltip content="缩写" placement="top">
                <el-button @click="handleFloatingAI('condense')">📉</el-button>
              </el-tooltip>
              <el-tooltip content="改写" placement="top">
                <el-button @click="handleFloatingAI('rewrite')">🔄</el-button>
              </el-tooltip>
              <el-tooltip content="翻译英文" placement="top">
                <el-button @click="handleFloatingAI('translate_en')">🇬🇧</el-button>
              </el-tooltip>
              <el-tooltip content="翻译中文" placement="top">
                <el-button @click="handleFloatingAI('translate_zh')">🇨🇳</el-button>
              </el-tooltip>
              <el-tooltip content="AI问答" placement="top">
                <el-button @click="openAIChat">💬</el-button>
              </el-tooltip>
            </el-button-group>
          </div>
        </transition>
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
    
    <!-- AI 助手组件 -->
    <AIAssistant 
      v-model="showAIDialog" 
      :text="aiSelectedText" 
      :action="aiAction"
      @apply="handleAIApply"
    />
    
    <!-- AI 问答组件 -->
    <AIChat
      v-model="showAIChatDialog"
      :context="aiChatContext"
      @insert="handleAIChatInsert"
    />
    
    <!-- 大纲生成器 -->
    <OutlineGenerator
      v-model="showOutlineGenerator"
      @apply="handleOutlineApply"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Clock, Document, ArrowDown, View, FolderOpened, Close, Check, Download, Loading, CircleCheck, CircleClose, Warning, CopyDocument, MagicStick, List } from '@element-plus/icons-vue'
import { useDraftStore } from '@/stores/draft'
import { useFileStore } from '@/stores/file'
import { previewFile, type FilePreview } from '@/api/files'
import { formatDate, formatFileSize } from '@/utils/format'
import { exportReport, type ExportFormat } from '@/utils/export'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import AIAssistant from '@/components/AIAssistant.vue'
import AIChat from '@/components/AIChat.vue'
import OutlineGenerator from '@/components/OutlineGenerator.vue'
import type { AIAction } from '@/api/ai'
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

// AI 助手相关
const showAIDialog = ref(false)
const aiSelectedText = ref('')
const aiAction = ref<AIAction>('polish')
const aiReplaceMode = ref(false)  // 是否替换选中文本模式

// 浮动工具栏相关
const editorPanelRef = ref<HTMLElement>()
const showFloatingToolbar = ref(false)
const selectedText = ref('')
const floatingToolbarStyle = ref({ top: '0px', left: '0px' })

// AI 问答相关
const showAIChatDialog = ref(false)
const aiChatContext = ref('')

// 大纲生成相关
const showOutlineGenerator = ref(false)

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
  try { 
    console.log('开始加载文件预览，文件ID:', fileId)
    const result = await previewFile(fileId)
    console.log('文件预览结果:', result)
    previewData.value = result
    
    if (!result.preview_available) {
      ElMessage.warning(result.message || '该文件类型不支持预览')
    }
  }
  catch (error) { 
    console.error('文件预览加载失败:', error)
    previewData.value = { 
      file_id: fileId, 
      filename: '', 
      preview_available: false, 
      content: null, 
      message: '加载失败，请检查网络连接' 
    }
    ElMessage.error('文件预览加载失败')
  }
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

// 处理文本选中事件
const handleTextSelection = (text: string) => {
  if (text && text.trim().length > 0) {
    selectedText.value = text.trim()
    showFloatingToolbar.value = true
    
    // 计算浮动工具栏位置
    const selection = window.getSelection()
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      const panelRect = editorPanelRef.value?.getBoundingClientRect()
      
      if (panelRect) {
        floatingToolbarStyle.value = {
          top: `${rect.top - panelRect.top - 45}px`,
          left: `${rect.left - panelRect.left + rect.width / 2}px`
        }
      }
    }
  } else {
    // 延迟隐藏，避免点击工具栏时立即消失
    setTimeout(() => {
      if (!selectedText.value) {
        showFloatingToolbar.value = false
      }
    }, 200)
  }
}

// 浮动工具栏 AI 操作
const handleFloatingAI = (action: AIAction) => {
  if (!selectedText.value) return
  
  aiAction.value = action
  aiSelectedText.value = selectedText.value
  aiReplaceMode.value = true  // 标记为替换模式
  showAIDialog.value = true
  showFloatingToolbar.value = false
}

// 打开 AI 问答对话框
const openAIChat = () => {
  // 如果有选中文本，作为上下文
  const currentSelection = markdownEditorRef.value?.getSelection()
  aiChatContext.value = currentSelection?.trim() || selectedText.value || ''
  showAIChatDialog.value = true
  showFloatingToolbar.value = false
}

// AI 问答结果插入
const handleAIChatInsert = (text: string) => {
  if (markdownEditorRef.value) {
    markdownEditorRef.value.insertValue('\n\n' + text + '\n\n')
    handleContentChange()
  }
}

// 大纲应用到编辑器
const handleOutlineApply = async (outline: string) => {
  if (!markdownEditorRef.value) return
  
  // 如果编辑器为空，直接设置
  if (!editorContent.value.trim()) {
    markdownEditorRef.value.setValue(outline)
    ElMessage.success('大纲已应用')
  } else {
    // 如果编辑器有内容，询问用户
    try {
      await ElMessageBox.confirm(
        '编辑器中已有内容，是否要替换？',
        '确认操作',
        {
          confirmButtonText: '替换',
          cancelButtonText: '追加到末尾',
          distinguishCancelAndClose: true,
          type: 'warning'
        }
      )
      // 用户选择替换
      markdownEditorRef.value.setValue(outline)
      ElMessage.success('大纲已替换')
    } catch (action) {
      if (action === 'cancel') {
        // 用户选择追加
        markdownEditorRef.value.insertValue('\n\n' + outline)
        ElMessage.success('大纲已追加到末尾')
      }
      // action === 'close' 时不做任何操作
    }
  }
  handleContentChange()
}

// AI 助手功能（顶部菜单）
const handleAIAction = async (action: AIAction) => {
  // 问答模式单独处理
  if (action === 'ask') {
    openAIChat()
    return
  }
  
  aiAction.value = action
  aiReplaceMode.value = false  // 顶部菜单不是替换模式
  
  // 先检查是否有选中的文本
  const currentSelection = markdownEditorRef.value?.getSelection()
  if (currentSelection && currentSelection.trim().length > 0) {
    aiSelectedText.value = currentSelection.trim()
    aiReplaceMode.value = true  // 有选中文本时使用替换模式
    showAIDialog.value = true
    return
  }
  
  // 续写操作：直接使用最后500字作为上下文
  if (action === 'continue') {
    const content = editorContent.value
    if (!content.trim()) {
      ElMessage.warning('请先输入一些内容')
      return
    }
    aiSelectedText.value = content.slice(-500)
    showAIDialog.value = true
    return
  }
  
  // 其他操作：弹出输入框让用户输入要处理的文本
  try {
    const { value } = await ElMessageBox.prompt(
      '请输入或粘贴要处理的文本（建议 2000 字以内）',
      `AI ${actionNames[action]}`,
      {
        confirmButtonText: '开始处理',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '在此输入要处理的文本...',
        inputValidator: (val) => {
          if (!val?.trim()) return '请输入文本内容'
          if (val.length > 3000) return '文本过长，请控制在 3000 字以内'
          return true
        }
      }
    )
    
    aiSelectedText.value = value.trim()
    showAIDialog.value = true
  } catch {
    // 用户取消
  }
}

// AI 操作名称映射
const actionNames: Record<AIAction, string> = {
  polish: '润色',
  expand: '扩写',
  condense: '缩写',
  rewrite: '改写',
  continue: '续写',
  explain: '解释',
  translate_en: '翻译英文',
  translate_zh: '翻译中文',
  custom: '处理',
  ask: '问答',
  outline: '大纲生成'
}

// AI 结果应用
const handleAIApply = (result: string) => {
  if (!markdownEditorRef.value) return
  
  // 续写：在末尾追加
  if (aiAction.value === 'continue') {
    markdownEditorRef.value.insertValue('\n\n' + result)
    ElMessage.success('续写内容已添加到文末')
  } else if (aiReplaceMode.value) {
    // 替换模式：替换选中的文本
    markdownEditorRef.value.replaceSelection(result)
    ElMessage.success('已替换选中文本')
  } else {
    // 其他操作：插入到光标位置
    markdownEditorRef.value.insertValue('\n\n' + result + '\n\n')
    ElMessage.success('AI 生成的内容已插入，请根据需要调整')
  }
  
  // 重置状态
  selectedText.value = ''
  aiReplaceMode.value = false
  handleContentChange()
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
.draft-editor { 
  height: 100vh; 
  display: flex; 
  flex-direction: column; 
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  overflow: hidden; 
}

.editor-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 12px 20px; 
  background: linear-gradient(to right, #ffffff 0%, #fafbfc 100%);
  border-bottom: 1px solid #e4e7ed; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  flex-shrink: 0; 
}

.header-left { 
  display: flex; 
  align-items: center; 
  gap: 14px; 
}

.header-left .el-divider { 
  height: 28px; 
  margin: 0 4px;
}

.draft-info h3 { 
  margin: 0 0 4px 0; 
  color: #1f2937; 
  font-size: 16px; 
  font-weight: 600; 
  max-width: 350px; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  white-space: nowrap;
  letter-spacing: 0.3px;
}

.meta-info { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  font-size: 12px; 
  color: #6b7280; 
}

.header-right { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  flex-shrink: 0; 
}

.save-status { 
  display: flex; 
  align-items: center; 
  gap: 5px; 
  padding: 4px 10px; 
  border-radius: 6px; 
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}
.save-status.status-saving { 
  color: #3b82f6; 
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}
.save-status.status-saved { 
  color: #10b981; 
  background: #d1fae5;
  border: 1px solid #a7f3d0;
}
.save-status.status-error { 
  color: #ef4444; 
  background: #fee2e2;
  border: 1px solid #fecaca;
}
.save-status.status-unsaved { 
  color: #f59e0b; 
  background: #fef3c7;
  border: 1px solid #fde68a;
}

.editor-main { 
  flex: 1; 
  display: flex; 
  gap: 18px; 
  padding: 18px 20px; 
  overflow: hidden; 
}

.editor-panel { 
  flex: 1; 
  background: white; 
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.1);
  overflow: hidden; 
  position: relative;
  transition: box-shadow 0.3s;
}

.editor-panel:hover {
  box-shadow: 0 6px 16px rgba(0,0,0,0.12), 0 0 1px rgba(0,0,0,0.1);
}

/* 浮动 AI 工具栏 */
.floating-ai-toolbar {
  position: absolute;
  z-index: 1000;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4), 0 2px 8px rgba(0,0,0,0.1);
  padding: 6px;
  backdrop-filter: blur(10px);
}

.floating-ai-toolbar .el-button-group .el-button {
  padding: 8px 12px;
  font-size: 15px;
  background: rgba(255,255,255,0.95);
  border: none;
  transition: all 0.2s;
}

.floating-ai-toolbar .el-button-group .el-button:hover {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.floating-ai-toolbar::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #764ba2;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.2s, transform 0.2s; 
}
.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
  transform: translateX(-50%) translateY(-8px) scale(0.95); 
}

.data-panel { 
  width: 400px; 
  background: white; 
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.1);
  display: flex; 
  flex-direction: column;
  transition: box-shadow 0.3s;
}

.data-panel:hover {
  box-shadow: 0 6px 16px rgba(0,0,0,0.12), 0 0 1px rgba(0,0,0,0.1);
}

.data-panel-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 14px 16px; 
  border-bottom: 1px solid #e5e7eb; 
  background: linear-gradient(to bottom, #fafbfc 0%, #f9fafb 100%);
  border-radius: 12px 12px 0 0;
}

.data-panel-header h4 { 
  margin: 0; 
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  letter-spacing: 0.3px;
}

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
  padding: 10px 14px; 
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-bottom: 1px solid #bfdbfe; 
}

.file-info-bar .file-name { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  font-size: 13px; 
  color: #1e40af;
  font-weight: 500;
}

.preview-loading, .preview-error { 
  padding: 20px; 
}
.preview-content { 
  flex: 1; 
  overflow: auto; 
  padding: 14px; 
  background: #f9fafb; 
}

.preview-content pre { 
  margin: 0; 
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace; 
  font-size: 13px; 
  line-height: 1.7; 
  white-space: pre-wrap; 
  word-break: break-all;
  color: #1f2937;
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s;
}

.preview-content pre:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.version-list { 
  max-height: 450px; 
  overflow-y: auto; 
  padding: 4px;
}

.version-item { 
  padding: 14px 16px; 
  border-bottom: 1px solid #f3f4f6;
  border-radius: 8px;
  margin-bottom: 6px;
  transition: all 0.2s;
}

.version-item:hover {
  background: #f9fafb;
  transform: translateX(2px);
}

.version-item.current { 
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-left: 4px solid #3b82f6;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.15);
}

.version-header { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 6px;
  align-items: center;
}

.version-header strong {
  color: #1f2937;
  font-size: 14px;
}

.version-summary { 
  color: #6b7280; 
  font-size: 13px; 
  margin-bottom: 10px;
  line-height: 1.5;
}

.file-list { 
  max-height: 350px; 
  overflow-y: auto; 
  padding: 4px;
}

.file-item { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 12px 14px; 
  border-radius: 8px; 
  cursor: pointer; 
  border: 2px solid transparent;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.file-item:hover { 
  background: #f9fafb;
  border-color: #e5e7eb;
  transform: translateX(2px);
}

.file-item.selected { 
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.file-details { 
  flex: 1; 
}

.file-details div {
  color: #1f2937;
  font-weight: 500;
  margin-bottom: 2px;
}

.file-details small { 
  color: #6b7280;
  font-size: 12px;
}

.check { 
  color: #10b981;
  font-size: 18px;
}
</style>
