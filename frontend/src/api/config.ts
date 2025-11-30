import request from './request'
import type { AppConfig } from '@/types'

export const getAppConfig = () => {
  return request<AppConfig>({ url: '/config', method: 'get' })
}
