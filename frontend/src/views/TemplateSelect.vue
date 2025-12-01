<template>
  <div class="template-select">
    <div class="header">
      <div class="header-top">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <el-button @click="goToDraftBox">
          <el-icon><Folder /></el-icon> 草稿箱
        </el-button>
      </div>
      <h2>选择模板</h2>
      <p>请选择一个模板开始撰写报告</p>
    </div>

    <div class="template-grid">
      <div class="template-card blank-template" @click="selectTemplate(null)">
        <div class="template-icon">
          <el-icon size="48"><Document /></el-icon>
        </div>
        <h3>空白模板</h3>
        <p>从空白页面开始撰写</p>
      </div>

      <div 
        v-for="template in templateFiles" 
        :key="template.id"
        class="template-card"
        @click="selectTemplate(template)"
      >
        <div class="template-icon">
          <el-icon size="48"><Files /></el-icon>
        </div>
        <h3>{{ template.filename }}</h3>
        <p>{{ formatFileSize(template.file_size) }}</p>
      </div>
    </div>

    <div v-if="templateFiles.length === 0" class="empty-state">
      <el-empty description="暂无模板文件">
        <el-button type="primary" @click="goToUpload">上传模板文件</el-button>
      </el-empty>
    </div>

    <el-dialog v-model="showCreateDialog" title="创建报告" width="500px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="报告标题" required>
          <el-input v-model="createForm.title" placeholder="请输入报告标题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createDraft" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Files, ArrowLeft, Folder } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/file'
import { useDraftStore } from '@/stores/draft'
import { formatFileSize } from '@/utils/format'
import type { File } from '@/types'

const router = useRouter()
const fileStore = useFileStore()
const draftStore = useDraftStore()

const templateFiles = ref<File[]>([])
const selectedTemplate = ref<File | null>(null)
const showCreateDialog = ref(false)
const creating = ref(false)
const createForm = ref({ title: '' })

const fetchTemplateFiles = async () => {
  await fileStore.fetchFiles()
  templateFiles.value = fileStore.files.filter(f => String(f.file_type).toUpperCase() === 'TEMPLATE')
}

const selectTemplate = (template: File | null) => {
  selectedTemplate.value = template
  createForm.value.title = template ? `基于${template.filename}的报告` : '新报告'
  showCreateDialog.value = true
}

const createDraft = async () => {
  if (!createForm.value.title.trim()) return
  
  try {
    creating.value = true
    const draft = await draftStore.createDraft({
      title: createForm.value.title,
      template_file_id: selectedTemplate.value?.id,
      content: ''
    })
    router.push(`/draft-editor/${draft.id}`)
  } finally {
    creating.value = false
  }
}

const goToUpload = () => router.push('/')
const goBack = () => router.push('/')
const goToDraftBox = () => router.push('/draft-box')

onMounted(() => fetchTemplateFiles())
</script>

<style scoped>
.template-select { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header { text-align: center; margin-bottom: 40px; }
.header-top { display: flex; justify-content: space-between; margin-bottom: 20px; }
.header h2 { color: #303133; margin-bottom: 8px; }
.header p { color: #606266; font-size: 14px; }
.template-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.template-card { border: 2px solid #e4e7ed; border-radius: 8px; padding: 24px; text-align: center; cursor: pointer; transition: all 0.3s; background: white; }
.template-card:hover { border-color: #409eff; box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15); transform: translateY(-2px); }
.blank-template { border-style: dashed; border-color: #409eff; background: #f0f9ff; }
.template-icon { color: #409eff; margin-bottom: 16px; }
.template-card h3 { color: #303133; margin: 0 0 8px 0; font-size: 16px; }
.template-card p { color: #606266; margin: 0; font-size: 14px; }
.empty-state { text-align: center; padding: 40px; }
</style>
