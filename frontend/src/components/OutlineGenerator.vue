<template>
  <el-dialog 
    v-model="visible" 
    title="📋 智能大纲生成" 
    width="650px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="outline-generator">
      <!-- 输入表单 -->
      <el-form v-if="!generated" :model="form" label-width="100px" label-position="top">
        <el-form-item label="报告主题" required>
          <el-input
            v-model="form.topic"
            placeholder="例如：2024年第一季度销售分析报告"
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item label="报告类型">
          <el-select v-model="form.report_type" placeholder="选择报告类型" :disabled="loading" style="width: 100%">
            <el-option label="商业报告" value="商业报告" />
            <el-option label="技术报告" value="技术报告" />
            <el-option label="研究报告" value="研究报告" />
            <el-option label="项目报告" value="项目报告" />
            <el-option label="分析报告" value="分析报告" />
            <el-option label="总结报告" value="总结报告" />
            <el-option label="学术论文" value="学术论文" />
            <el-option label="通用报告" value="通用报告" />
          </el-select>
        </el-form-item>

        <el-form-item label="目标受众">
          <el-select v-model="form.audience" placeholder="选择目标受众" :disabled="loading" style="width: 100%">
            <el-option label="管理层" value="管理层" />
            <el-option label="技术人员" value="技术人员" />
            <el-option label="客户" value="客户" />
            <el-option label="投资者" value="投资者" />
            <el-option label="学术界" value="学术界" />
            <el-option label="一般读者" value="一般读者" />
          </el-select>
        </el-form-item>

        <el-form-item label="其他要求">
          <el-input
            v-model="form.additional_requirements"
            type="textarea"
            :rows="3"
            placeholder="例如：需要包含数据分析章节、重点关注市场趋势、包含风险评估等（可选）"
            :disabled="loading"
          />
        </el-form-item>
      </el-form>

      <!-- 生成结果 -->
      <div v-else class="outline-result">
        <div class="result-header">
          <span class="result-title">✅ 大纲生成成功</span>
          <el-button size="small" @click="regenerate" :loading="loading">
            <el-icon><Refresh /></el-icon> 重新生成
          </el-button>
        </div>
        <div class="outline-preview">
          <div v-html="renderedOutline" class="markdown-content"></div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>AI 正在生成大纲，请稍候...</p>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="loading">取消</el-button>
        <el-button v-if="!generated" type="primary" @click="generateOutline" :loading="loading" :disabled="!form.topic.trim()">
          <el-icon><MagicStick /></el-icon> 生成大纲
        </el-button>
        <el-button v-else type="success" @click="applyOutline" :disabled="loading">
          <el-icon><Check /></el-icon> 应用到编辑器
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Refresh, MagicStick, Check } from '@element-plus/icons-vue'
import { processAI } from '@/api/ai'
import { marked } from 'marked'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'apply', outline: string): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = ref({
  topic: '',
  report_type: '通用报告',
  audience: '一般读者',
  additional_requirements: ''
})

const loading = ref(false)
const generated = ref(false)
const outlineText = ref('')

const renderedOutline = computed(() => {
  if (!outlineText.value) return ''
  return marked(outlineText.value)
})

const generateOutline = async () => {
  if (!form.value.topic.trim()) {
    ElMessage.warning('请输入报告主题')
    return
  }

  loading.value = true
  try {
    const params = JSON.stringify({
      topic: form.value.topic,
      report_type: form.value.report_type,
      audience: form.value.audience,
      additional_requirements: form.value.additional_requirements
    })

    const response = await processAI({
      text: '',
      action: 'outline',
      custom_prompt: params
    })

    if (response.success) {
      outlineText.value = response.result
      generated.value = true
      ElMessage.success('大纲生成成功')
    } else {
      throw new Error('生成失败')
    }
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || err?.message || '大纲生成失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const regenerate = () => {
  generated.value = false
  outlineText.value = ''
}

const applyOutline = () => {
  if (outlineText.value) {
    emit('apply', outlineText.value)
    handleClose()
    ElMessage.success('大纲已应用到编辑器')
  }
}

const handleClose = () => {
  if (!loading.value) {
    visible.value = false
    // 延迟重置，避免关闭动画时看到内容变化
    setTimeout(() => {
      generated.value = false
      outlineText.value = ''
      form.value = {
        topic: '',
        report_type: '通用报告',
        audience: '一般读者',
        additional_requirements: ''
      }
    }, 300)
  }
}
</script>

<style scoped>
.outline-generator {
  position: relative;
  min-height: 200px;
}

.outline-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border-radius: 8px;
  border: 1px solid #6ee7b7;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #065f46;
}

.outline-preview {
  max-height: 450px;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.markdown-content {
  color: #1f2937;
  line-height: 1.8;
}

.markdown-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 20px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.markdown-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 16px 0 10px 0;
}

.markdown-content :deep(h3) {
  font-size: 17px;
  font-weight: 600;
  color: #374151;
  margin: 14px 0 8px 0;
}

.markdown-content :deep(h4) {
  font-size: 15px;
  font-weight: 600;
  color: #4b5563;
  margin: 12px 0 6px 0;
}

.markdown-content :deep(p) {
  margin: 8px 0;
  color: #6b7280;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
  color: #6b7280;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  border-radius: 8px;
  z-index: 10;
}

.loading-overlay p {
  color: #6b7280;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
