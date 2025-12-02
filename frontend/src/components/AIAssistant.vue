<template>
  <div class="ai-assistant">
    <el-dialog 
      v-model="visible" 
      :title="dialogTitle" 
      width="650px"
      :close-on-click-modal="false"
      @close="handleClose"
    >
      <div class="ai-content">
        <!-- 原文显示 -->
        <div class="original-section">
          <div class="section-label">
            <span>📄 原文</span>
            <span class="text-count">{{ originalText.length }} 字</span>
          </div>
          <div class="text-box original">{{ originalText }}</div>
        </div>

        <!-- AI 结果 -->
        <div class="result-section">
          <div class="section-label">
            <span>🤖 AI {{ actionName }}结果</span>
            <el-tag v-if="loading" type="warning" size="small">
              <el-icon class="is-loading"><Loading /></el-icon> 生成中...
            </el-tag>
            <el-tag v-else-if="result && !error" type="success" size="small">✓ 完成</el-tag>
            <el-tag v-else-if="error" type="danger" size="small">✗ 失败</el-tag>
          </div>
          
          <div class="result-box" :class="{ loading, error: !!error }">
            <!-- 加载状态 -->
            <div v-if="loading" class="loading-state">
              <el-icon class="is-loading" :size="32"><Loading /></el-icon>
              <p>AI 正在处理中，请稍候...</p>
              <p class="hint">这可能需要几秒钟</p>
            </div>
            
            <!-- 错误状态 -->
            <div v-else-if="error" class="error-state">
              <el-alert :title="error" type="error" show-icon :closable="false" />
            </div>
            
            <!-- 结果显示 -->
            <div v-else-if="result" class="result-text">{{ result }}</div>
            
            <!-- 等待状态 -->
            <div v-else class="waiting-state">
              <p>点击下方按钮开始生成</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="startGenerate" :loading="loading" type="warning">
            <el-icon><Refresh /></el-icon> {{ result ? '重新生成' : '开始生成' }}
          </el-button>
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="handleApply" :disabled="!result || loading">
            <el-icon><Check /></el-icon> 应用到编辑器
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Refresh, Check } from '@element-plus/icons-vue'
import { processAI, type AIAction } from '@/api/ai'

const props = defineProps<{
  modelValue: boolean
  text: string
  action: AIAction
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'apply', result: string): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const originalText = ref('')
const result = ref('')
const loading = ref(false)
const error = ref('')

const actionNames: Record<AIAction, string> = {
  polish: '润色',
  expand: '扩写',
  condense: '缩写',
  rewrite: '改写',
  continue: '续写',
  explain: '解释',
  translate_en: '翻译英文',
  translate_zh: '翻译中文',
  custom: '处理'
}

const actionName = computed(() => actionNames[props.action] || '处理')
const dialogTitle = computed(() => `AI ${actionName.value}`)

// 监听显示状态和文本变化
watch([() => props.modelValue, () => props.text], ([visible, text]) => {
  if (visible && text) {
    originalText.value = text
    result.value = ''
    error.value = ''
  }
}, { immediate: true })

// 开始生成
const startGenerate = async () => {
  if (!originalText.value || loading.value) return
  
  loading.value = true
  result.value = ''
  error.value = ''
  
  try {
    console.log('开始调用 AI API...', { text: originalText.value.slice(0, 50), action: props.action })
    
    const response = await processAI({
      text: originalText.value,
      action: props.action
    })
    
    console.log('AI API 响应:', response)
    
    if (response.success) {
      result.value = response.result
      ElMessage.success('AI 生成完成')
    } else {
      throw new Error('生成失败')
    }
  } catch (err: any) {
    console.error('AI API 错误:', err)
    error.value = err?.response?.data?.detail || err?.message || 'AI 处理失败，请重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const handleApply = () => {
  if (result.value) {
    emit('apply', result.value)
    handleClose()
  }
}

const handleClose = () => {
  visible.value = false
  result.value = ''
  error.value = ''
  loading.value = false
}
</script>

<style scoped>
.ai-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.text-count {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.text-box, .result-box {
  padding: 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.7;
}

.text-box.original {
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #e4e7ed;
  max-height: 120px;
  overflow-y: auto;
}

.result-box {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-box.loading {
  background: #fafafa;
  border-color: #e4e7ed;
}

.result-box.error {
  background: #fef0f0;
  border-color: #fbc4c4;
}

.loading-state, .waiting-state, .error-state {
  text-align: center;
  color: #909399;
}

.loading-state p {
  margin: 8px 0 0;
}

.loading-state .hint {
  font-size: 12px;
  color: #c0c4cc;
}

.result-text {
  white-space: pre-wrap;
  word-break: break-word;
  width: 100%;
  align-self: flex-start;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
