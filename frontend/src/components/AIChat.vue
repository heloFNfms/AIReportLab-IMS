<template>
  <el-dialog 
    v-model="visible" 
    title="💬 AI 问答助手" 
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="ai-chat">
      <!-- 上下文显示 -->
      <div v-if="contextText" class="context-section">
        <div class="section-label">
          <span>📄 参考内容</span>
          <el-button size="small" text type="danger" @click="clearContext">
            <el-icon><Close /></el-icon> 清除
          </el-button>
        </div>
        <div class="context-box">{{ contextText }}</div>
      </div>

      <!-- 对话历史 -->
      <div class="chat-history" ref="chatHistoryRef">
        <div v-if="messages.length === 0" class="empty-chat">
          <p>👋 你好！我是 AI 助手</p>
          <p class="hint">你可以向我提问，或者选中文本后让我帮你分析</p>
        </div>
        <div v-for="(msg, idx) in messages" :key="idx" class="chat-message" :class="msg.role">
          <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
          </div>
        </div>
        <div v-if="loading" class="chat-message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text loading-text">
              <el-icon class="is-loading"><Loading /></el-icon> 思考中...
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入你的问题..."
          :disabled="loading"
          @keydown.enter.ctrl="sendMessage"
        />
        <div class="input-actions">
          <span class="hint">Ctrl + Enter 发送</span>
          <el-button type="primary" @click="sendMessage" :loading="loading" :disabled="!inputText.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="clearChat" :disabled="messages.length === 0">清空对话</el-button>
        <el-button v-if="lastAssistantMessage" type="success" @click="handleInsert">
          <el-icon><DocumentAdd /></el-icon> 插入最后回复
        </el-button>
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Close, DocumentAdd } from '@element-plus/icons-vue'
import { processAI } from '@/api/ai'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const props = defineProps<{
  modelValue: boolean
  context?: string  // 选中的文本作为上下文
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'insert', text: string): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const contextText = ref('')
const inputText = ref('')
const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const chatHistoryRef = ref<HTMLElement>()

const lastAssistantMessage = computed(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'assistant') {
      return messages.value[i].content
    }
  }
  return ''
})

// 监听显示状态，初始化上下文
watch(() => props.modelValue, (val) => {
  if (val && props.context) {
    contextText.value = props.context
  }
})

const clearContext = () => {
  contextText.value = ''
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  const question = inputText.value.trim()
  if (!question || loading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: question })
  inputText.value = ''
  scrollToBottom()

  loading.value = true
  try {
    const response = await processAI({
      text: contextText.value || '',
      action: 'ask',
      custom_prompt: question
    })

    if (response.success) {
      messages.value.push({ role: 'assistant', content: response.result })
      scrollToBottom()
    } else {
      throw new Error('请求失败')
    }
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || err?.message || 'AI 请求失败'
    messages.value.push({ role: 'assistant', content: `❌ 错误: ${errorMsg}` })
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const clearChat = () => {
  messages.value = []
}

const handleInsert = () => {
  if (lastAssistantMessage.value) {
    emit('insert', lastAssistantMessage.value)
    ElMessage.success('已插入到编辑器')
  }
}

const handleClose = () => {
  visible.value = false
}
</script>


<style scoped>
.ai-chat {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.context-section .section-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 6px;
}

.context-box {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13px;
  color: #606266;
  max-height: 80px;
  overflow-y: auto;
  line-height: 1.5;
}

.chat-history {
  min-height: 200px;
  max-height: 350px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  background: #fafafa;
}

.empty-chat {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}
.empty-chat p { margin: 8px 0; }
.empty-chat .hint { font-size: 13px; color: #c0c4cc; }

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.chat-message:last-child { margin-bottom: 0; }

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.chat-message.user .message-avatar { background: #ecf5ff; }
.chat-message.assistant .message-avatar { background: #f0f9eb; }

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  background: white;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.chat-message.user .message-text {
  background: #409eff;
  color: white;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.input-actions .hint {
  font-size: 12px;
  color: #c0c4cc;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
