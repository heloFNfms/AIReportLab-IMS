<template>
  <div class="markdown-editor" ref="editorContainer">
    <div :id="editorId" class="vditor-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  height?: number | string
  mode?: 'wysiwyg' | 'ir' | 'sv'  // 所见即所得 | 即时渲染 | 分屏预览
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const editorContainer = ref<HTMLElement>()
const editorId = `vditor-${Date.now()}`
let vditor: Vditor | null = null
let isInternalChange = false
let isEditorReady = false
let pendingValue: string | null = null

const initEditor = () => {
  const container = document.getElementById(editorId)
  if (!container) return

  vditor = new Vditor(editorId, {
    height: props.height || '100%',
    mode: props.mode || 'ir',
    placeholder: props.placeholder || '开始撰写你的报告...',
    theme: 'classic',
    icon: 'material',
    cache: { enable: false },
    preview: {
      theme: { current: 'light' },
      hljs: { style: 'github' },
      markdown: { toc: true }
    },
    toolbar: [
      'emoji', 'headings', 'bold', 'italic', 'strike', 'link', '|',
      'list', 'ordered-list', 'check', 'outdent', 'indent', '|',
      'quote', 'line', 'code', 'inline-code', 'insert-before', 'insert-after', '|',
      'table', 'upload', '|',
      'undo', 'redo', '|',
      'fullscreen', 'edit-mode', 'outline', 'preview', 'export'
    ],
    toolbarConfig: {
      pin: true
    },
    counter: {
      enable: true,
      type: 'text'
    },
    outline: {
      enable: true,
      position: 'right'
    },
    after: () => {
      isEditorReady = true
      // 设置初始值或待处理的值
      const valueToSet = pendingValue !== null ? pendingValue : props.modelValue
      if (vditor && valueToSet) {
        vditor.setValue(valueToSet)
      }
      pendingValue = null
    },
    input: (value: string) => {
      isInternalChange = true
      emit('update:modelValue', value)
      emit('change', value)
      nextTick(() => {
        isInternalChange = false
      })
    },
    upload: {
      accept: 'image/*',
      handler: (files: File[]) => {
        // 简单处理：转为 base64
        files.forEach(file => {
          const reader = new FileReader()
          reader.onload = (e) => {
            const base64 = e.target?.result as string
            if (vditor && isEditorReady) {
              vditor.insertValue(`![${file.name}](${base64})`)
            }
          }
          reader.readAsDataURL(file)
        })
        return null
      }
    }
  })
}

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (isInternalChange) return
  
  // 如果编辑器还没准备好，保存待处理的值
  if (!isEditorReady || !vditor) {
    pendingValue = newVal || ''
    return
  }
  
  // 编辑器已就绪，直接设置值
  if (newVal !== vditor.getValue()) {
    vditor.setValue(newVal || '')
  }
})

// 获取编辑器实例
const getVditor = () => vditor

// 获取 HTML 内容
const getHTML = () => vditor?.getHTML() || ''

// 获取 Markdown 内容
const getValue = () => vditor?.getValue() || ''

// 设置内容
const setValue = (value: string) => {
  if (isEditorReady && vditor) {
    vditor.setValue(value)
  } else {
    pendingValue = value
  }
}

// 插入内容
const insertValue = (value: string) => {
  vditor?.insertValue(value)
}

// 聚焦
const focus = () => {
  vditor?.focus()
}

defineExpose({
  getVditor,
  getHTML,
  getValue,
  setValue,
  insertValue,
  focus
})

onMounted(() => {
  nextTick(() => {
    initEditor()
  })
})

onBeforeUnmount(() => {
  isEditorReady = false
  vditor?.destroy()
  vditor = null
})
</script>

<style scoped>
.markdown-editor {
  width: 100%;
  height: 100%;
}

.vditor-container {
  width: 100%;
  height: 100%;
}

/* 自定义 Vditor 样式 */
:deep(.vditor) {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.vditor-toolbar) {
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  padding: 4px 8px;
}

:deep(.vditor-content) {
  background: white;
}

:deep(.vditor-ir) {
  padding: 16px 20px;
}

:deep(.vditor-wysiwyg) {
  padding: 16px 20px;
}

:deep(.vditor-sv) {
  padding: 0;
}

:deep(.vditor-outline) {
  border-left: 1px solid #e4e7ed;
  background: #fafafa;
}
</style>
