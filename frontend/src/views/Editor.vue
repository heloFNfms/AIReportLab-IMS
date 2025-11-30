<template>
  <el-container style="height: calc(100vh - 64px);">
    <el-main style="padding: 12px;">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-card shadow="never" style="height: calc(100vh - 96px); display: flex; flex-direction: column;">
            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <el-text tag="b">编辑器</el-text>
                <el-text style="margin-left: 8px;" type="info">模板ID：{{ templateId }}</el-text>
                <el-tag v-if="currentVersionNumber" size="small" style="margin-left: 8px;">v{{ currentVersionNumber }}</el-tag>
              </div>
              <div>
                <el-select v-model="editingStage" @change="changeEditingStage" size="small" style="width: 100px; margin-right: 8px;">
                  <el-option v-for="opt in editingStageOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
                <el-button size="small" @click="openVersionHistory">版本历史</el-button>
                <el-button type="primary" size="small" @click="manualSave">保存草稿</el-button>
                <el-button size="small" @click="exportMarkdown">导出 Markdown</el-button>
              </div>
            </div>
            <el-input
              v-model="content"
              type="textarea"
              :rows="28"
              placeholder="在此撰写文章内容"
              style="flex: 1;"
            />
            <div style="margin-top: 8px; display: flex; justify-content: space-between;">
              <el-text type="info">自动保存：{{ autosaveStatus }}</el-text>
              <el-text type="info">字数：{{ content.length }}</el-text>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" style="height: calc(100vh - 96px);">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <el-text tag="b">数据文件预览</el-text>
                </div>
                <div>
                  <el-select v-model="selectedFileId" placeholder="选择数据文件" style="width: 260px;" filterable>
                    <el-option
                      v-for="f in dataFiles"
                      :key="f.id"
                      :label="f.filename"
                      :value="f.id"
                    />
                  </el-select>
                  <el-button size="small" :disabled="!selectedFileId" @click="loadPreview" style="margin-left: 8px;">预览</el-button>
                </div>
              </div>
            </template>
            <div v-if="previewLoading" style="text-align:center; padding: 24px;">
              <el-text>正在加载预览...</el-text>
            </div>
            <div v-else style="height: 100%; overflow: auto;">
              <div v-if="preview?.preview_type === 'json'">
                <pre style="white-space: pre-wrap; word-break: break-all;">{{ formatJson(preview?.content) }}</pre>
              </div>
              <div v-else-if="preview?.preview_type === 'csv'">
                <el-table :data="csvRows" height="520" border>
                  <el-table-column v-for="(h, idx) in csvHeader" :key="idx" :prop="'col' + idx" :label="h">
                    <template #default="scope">
                      <span>{{ scope.row['col' + idx] }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <div v-else>
                <pre style="white-space: pre-wrap; word-break: break-all;">{{ preview?.content }}</pre>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="showVersionHistory" title="版本历史" width="60%">
      <el-table :data="versionList" v-loading="loadingVersions" max-height="400">
        <el-table-column prop="version_number" label="版本号" width="80" />
        <el-table-column prop="word_count" label="字数" width="80" />
        <el-table-column prop="change_summary" label="变更摘要" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="primary" @click="restoreVersion(scope.row.id)">恢复</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useFileStore } from '@/stores/file'
import { getTemplate } from '@/api/templates'
import { getDraft, saveDraft, getDraftVersions, restoreDraftVersion, updateEditingStage } from '@/api/reports'
import { previewFile } from '@/api/files'
import { templateToOutline } from '@/utils/templateToOutline'
import type { FileInfo, FilePreviewResponse, DraftVersion } from '@/types'

const route = useRoute()
const templateId = Number(route.params.templateId)

const content = ref('')
const autosaveStatus = ref('未保存')
let autosaveTimer: any = null

const fileStore = useFileStore()
const selectedFileId = ref<number | null>(null)
const preview = ref<FilePreviewResponse | null>(null)
const previewLoading = ref(false)

const dataFiles = ref<FileInfo[]>([])

const csvHeader = ref<string[]>([])
const csvRows = ref<Record<string, string>[]>([])

// 版本历史相关
const showVersionHistory = ref(false)
const versionList = ref<DraftVersion[]>([])
const loadingVersions = ref(false)

// 编辑阶段
const editingStage = ref<'draft' | 'reviewing' | 'completed'>('draft')
const editingStageOptions = [
  { label: '草稿', value: 'draft' },
  { label: '审阅中', value: 'reviewing' },
  { label: '已完成', value: 'completed' }
]

// 当前版本信息
const currentVersionNumber = ref<number | null>(null)
const draftId = ref<number | null>(null)

onMounted(async () => {
  // 加载模板结构并生成纲要
  try {
    const tpl: any = await getTemplate(templateId)
    const outline = templateToOutline(tpl.structure, tpl.name)
    if (!outline || outline.indexOf('#') < 0) {
      ElMessage.warning('解析到的纲要为空或不含标题')
    }
    // 加载草稿，若不存在使用纲要
    try {
      const draft = await getDraft(templateId)
      draftId.value = draft.id
      editingStage.value = draft.editing_stage
      if (draft.current_version) {
        content.value = draft.current_version.content || outline
        currentVersionNumber.value = draft.current_version.version_number
      } else {
        content.value = outline
      }
    } catch {
      content.value = outline
    }
  } catch (e) {
    ElMessage.error('加载模板失败')
  }

  // 加载数据文件列表
  await fileStore.fetchFiles()
  dataFiles.value = fileStore.files.filter(f => f.file_type === 'data')
})

// 自动保存草稿（停止输入1秒）
watch(content, (val) => {
  autosaveStatus.value = '未保存'
  if (autosaveTimer) clearTimeout(autosaveTimer)
  autosaveTimer = setTimeout(async () => {
    try {
      const result = await saveDraft({ 
        template_id: templateId, 
        content: val, 
        format: 'markdown',
        change_summary: '自动保存'
      })
      autosaveStatus.value = '已自动保存'
      if (result.current_version) {
        currentVersionNumber.value = result.current_version.version_number
      }
      if (!draftId.value) {
        draftId.value = result.id
      }
    } catch {
      autosaveStatus.value = '保存失败'
    }
  }, 1000)
})

function manualSave() {
  saveDraft({ 
    template_id: templateId, 
    content: content.value, 
    format: 'markdown',
    change_summary: '手动保存'
  })
    .then((result) => {
      ElMessage.success('草稿已保存')
      if (result.current_version) {
        currentVersionNumber.value = result.current_version.version_number
      }
    })
    .catch(() => ElMessage.error('草稿保存失败'))
}

function exportMarkdown() {
  const blob = new Blob([content.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `draft-${templateId}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function formatJson(obj: any) {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

async function loadPreview() {
  if (!selectedFileId.value) return
  previewLoading.value = true
  try {
    const res = await previewFile(selectedFileId.value)
    preview.value = res
    if (res.preview_type === 'csv' && res.csv_rows) {
      const header = res.csv_rows[0] || []
      csvHeader.value = header
      csvRows.value = (res.csv_rows.slice(1) || []).map(row => {
        const obj: Record<string, string> = {}
        header.forEach((h, i) => { obj['col' + i] = row[i] || '' })
        return obj
      })
    } else {
      csvHeader.value = []
      csvRows.value = []
    }
  } catch (e) {
    ElMessage.error('预览加载失败')
  } finally {
    previewLoading.value = false
  }
}

// 版本历史功能
async function openVersionHistory() {
  showVersionHistory.value = true
  loadingVersions.value = true
  try {
    const result = await getDraftVersions(templateId)
    versionList.value = result.versions
  } catch (e) {
    ElMessage.error('加载版本历史失败')
  } finally {
    loadingVersions.value = false
  }
}

async function restoreVersion(versionId: number) {
  try {
    const result = await restoreDraftVersion(templateId, versionId)
    if (result.current_version) {
      content.value = result.current_version.content
      currentVersionNumber.value = result.current_version.version_number
      ElMessage.success('版本已恢复')
      showVersionHistory.value = false
      // 刷新版本列表
      await openVersionHistory()
    }
  } catch (e) {
    ElMessage.error('恢复版本失败')
  }
}

async function changeEditingStage(newStage: 'draft' | 'reviewing' | 'completed') {
  try {
    await updateEditingStage(templateId, { editing_stage: newStage })
    editingStage.value = newStage
    ElMessage.success('编辑阶段已更新')
  } catch (e) {
    ElMessage.error('更新编辑阶段失败')
  }
}
</script>

<style scoped>
</style>
