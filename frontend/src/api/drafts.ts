import request from './request'
import type { Draft, DraftCreate, DraftUpdate, DraftVersion, DraftStatistics } from '@/types'

export const draftApi = {
  create: (data: DraftCreate) => {
    return request<Draft>({
      url: '/drafts/',
      method: 'post',
      data
    })
  },
  
  getList: (status?: string) => {
    return request<Draft[]>({
      url: '/drafts/',
      method: 'get',
      params: status ? { status_filter: status } : undefined
    })
  },
  
  getDetail: (id: number) => {
    return request<Draft & { versions: DraftVersion[] }>({
      url: `/drafts/${id}`,
      method: 'get'
    })
  },
  
  update: (id: number, data: DraftUpdate) => {
    return request<Draft>({
      url: `/drafts/${id}`,
      method: 'put',
      data
    })
  },
  
  complete: (id: number, data?: { title?: string; content?: string }) => {
    return request<Draft>({
      url: `/drafts/${id}/complete`,
      method: 'post',
      data
    })
  },
  
  reopen: (id: number) => {
    return request<Draft>({
      url: `/drafts/${id}/reopen`,
      method: 'post'
    })
  },
  
  getVersions: (id: number) => {
    return request<DraftVersion[]>({
      url: `/drafts/${id}/versions`,
      method: 'get'
    })
  },
  
  rollback: (id: number, version: number) => {
    return request<Draft>({
      url: `/drafts/${id}/rollback/${version}`,
      method: 'post'
    })
  },
  
  delete: (id: number) => {
    return request<{ message: string }>({
      url: `/drafts/${id}`,
      method: 'delete'
    })
  },
  
  getStatistics: () => {
    return request<DraftStatistics>({
      url: '/drafts/statistics',
      method: 'get'
    })
  }
}
