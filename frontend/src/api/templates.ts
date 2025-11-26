import request from './request'
import type { Template, TemplateCreate, TemplateUpdate } from '@/types'

export const createTemplate = (data: TemplateCreate) => {
  return request<Template>({ url: '/templates/', method: 'post', data })
}

export const getTemplates = () => {
  return request<Template[]>({ url: '/templates/', method: 'get' })
}

export const getTemplate = (id: number) => {
  return request<Template>({ url: `/templates/${id}`, method: 'get' })
}

export const updateTemplate = (id: number, data: TemplateUpdate) => {
  return request<Template>({ url: `/templates/${id}`, method: 'put', data })
}

export const analyzeTemplate = (id: number, force_reanalyze = false) => {
  return request<Template>({
    url: `/templates/${id}/analyze`,
    method: 'post',
    params: { force_reanalyze },
    timeout: 120000,
  })
}
