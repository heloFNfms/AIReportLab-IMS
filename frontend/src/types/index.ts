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
  TEMPLATE = 'TEMPLATE',
  DATA = 'DATA',
  OTHER = 'OTHER'
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
  total_reports: number  // 生成报告数
}

// API响应类型
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  detail?: string
}

// 草稿/报告相关类型
export interface Draft {
  id: number
  title: string
  user_id: number
  template_file_id?: number
  data_file_id?: number
  content?: string
  status: 'draft' | 'completed'
  current_version: number
  word_count: number
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface DraftVersion {
  id: number
  draft_id: number
  version: number
  content: string
  word_count: number
  change_summary?: string
  created_at: string
}

export interface DraftCreate {
  title: string
  template_file_id?: number
  data_file_id?: number
  content?: string
}

export interface DraftUpdate {
  title?: string
  content?: string
  data_file_id?: number
  change_summary?: string
}

export interface DraftStatistics {
  total: number
  draft_count: number
  completed_count: number
}

// 文件类型别名（兼容）
export type File = FileInfo
