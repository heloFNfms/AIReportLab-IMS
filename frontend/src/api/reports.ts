import request from './request'
import type {
  ReportCreateRequest,
  ReportGenerateRequest,
  Report,
  ReportStatusInfo,
  DraftSaveRequest,
  DraftWithContent,
  DraftVersionListResponse,
  DraftVersion,
  EditingStageUpdateRequest,
  Draft
} from '@/types'

export const generateReport = (data: ReportGenerateRequest) => {
  return request<Report>({ url: '/reports/generate', method: 'post', data })
}

export const getReports = () => {
  return request<Report[]>({ url: '/reports/', method: 'get' })
}

export const getReport = (id: number) => {
  return request<Report>({ url: `/reports/${id}`, method: 'get' })
}

export const getReportStatus = (id: number) => {
  return request<ReportStatusInfo>({ url: `/reports/${id}/status`, method: 'get' })
}

export const deleteReport = (id: number) => {
  return request<{ message: string }>({ url: `/reports/${id}`, method: 'delete' })
}

// 草稿管理API
export const saveDraft = (data: DraftSaveRequest) => {
  return request<DraftWithContent>({ url: '/reports/drafts', method: 'post', data })
}

export const getDraft = (templateId: number) => {
  return request<DraftWithContent>({ url: `/reports/drafts/${templateId}`, method: 'get' })
}

export const getDraftVersions = (templateId: number) => {
  return request<DraftVersionListResponse>({ url: `/reports/drafts/${templateId}/versions`, method: 'get' })
}

export const getDraftVersion = (templateId: number, versionId: number) => {
  return request<DraftVersion>({ url: `/reports/drafts/${templateId}/versions/${versionId}`, method: 'get' })
}

export const restoreDraftVersion = (templateId: number, versionId: number) => {
  return request<DraftWithContent>({ url: `/reports/drafts/${templateId}/restore/${versionId}`, method: 'post' })
}

export const updateEditingStage = (templateId: number, data: EditingStageUpdateRequest) => {
  return request<Draft>({ url: `/reports/drafts/${templateId}/stage`, method: 'put', data })
}
