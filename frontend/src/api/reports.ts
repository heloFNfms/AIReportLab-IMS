import request from './request'
import type { ReportCreateRequest, ReportGenerateRequest, Report, ReportStatusInfo } from '@/types'

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
