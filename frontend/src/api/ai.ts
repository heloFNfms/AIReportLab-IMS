import request from './request'

export type AIAction = 'polish' | 'expand' | 'condense' | 'rewrite' | 'continue' | 'explain' | 'translate_en' | 'translate_zh' | 'custom' | 'ask'

export interface AIRequest {
  text: string
  action: AIAction
  custom_prompt?: string
}

export interface AIResponse {
  success: boolean
  result: string
  action: string
}

export interface AIActionInfo {
  id: AIAction
  name: string
  description: string
  icon: string
}

/**
 * 非流式 AI 处理
 */
export const processAI = (data: AIRequest) => {
  return request<AIResponse>({
    url: '/ai/process',
    method: 'post',
    data,
    timeout: 60000  // AI 请求需要更长的超时时间
  })
}

/**
 * 流式 AI 处理
 * 返回一个可以读取流式响应的函数
 */
export const streamAI = async (
  data: AIRequest,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (error: string) => void
) => {
  const token = localStorage.getItem('token')
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  
  try {
    const response = await fetch(`${baseUrl}/ai/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应流')
    }

    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            onDone()
            return
          }
          if (data.startsWith('[ERROR]')) {
            onError(data.slice(8))
            return
          }
          onChunk(data)
        }
      }
    }
    
    onDone()
  } catch (error) {
    onError(error instanceof Error ? error.message : '请求失败')
  }
}

/**
 * 获取可用的 AI 操作列表
 */
export const getAIActions = () => {
  return request<{ actions: AIActionInfo[] }>({
    url: '/ai/actions',
    method: 'get'
  })
}
