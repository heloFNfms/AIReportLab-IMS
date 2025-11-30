// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface UserRegister {
  username: string
  email: string
  password: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

// 文件相关类型
export enum FileType {
  TEMPLATE = 'template',
  DATA = 'data',
  OTHER = 'other'
}

export interface FileInfo {
  id: number
  filename: string
  file_type: FileType
  file_size: number
  mime_type: string | null
  user_id: number
  is_oss: boolean
  oss_path: string | null
  oss_url: string | null
  created_at: string
  updated_at: string
}

export interface FileStatistics {
  total_files: number
  total_templates: number
  total_data_files: number
  total_size: number
}

export interface FilePreviewResponse {
  mime_type: string | null
  preview_type: 'json' | 'csv' | 'text'
  content?: any
  csv_rows?: string[][]
}

// 草稿相关类型
export interface DraftSaveRequest {
  template_id: number
  title?: string
  content: string
  format?: string
  change_summary?: string
}

export interface DraftVersion {
  id: number
  draft_id: number
  version_number: number
  content: string
  format: string
  change_summary: string | null
  word_count: number
  created_at: string
  created_by: number
}

export interface Draft {
  id: number
  template_id: number
  user_id: number
  title: string | null
  current_version_id: number | null
  editing_stage: 'draft' | 'reviewing' | 'completed'
  created_at: string
  updated_at: string
}

export interface DraftWithContent extends Draft {
  current_version: DraftVersion | null
}

export interface DraftVersionListResponse {
  versions: DraftVersion[]
  total: number
}

export interface EditingStageUpdateRequest {
  editing_stage: 'draft' | 'reviewing' | 'completed'
}

// 保留旧的DraftResponse用于向后兼容
export interface DraftResponse {
  template_id: number
  title?: string
  content: string
  format: 'markdown'
  updated_at: string
}

export interface AppConfig {
  featureFlags: {
    disableAIGeneration: boolean
  }
  uploadFolder: string
}

// API响应类型
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  detail?: string
}
