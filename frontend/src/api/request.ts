import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

// 定义request函数的返回类型，因为响应拦截器返回的是response.data
interface RequestInstance extends AxiosInstance {
  <T = any>(config: AxiosRequestConfig): Promise<T>
}

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError<any>) => {
    if (error.response) {
      const { status, data } = error.response
      const msg = (data && (data.detail || data.message)) || ''
      const show = (text: string) => ElMessage({ type: 'error', message: text, duration: 2500 })

      switch (status) {
        case 400:
          show(msg || '请求参数错误')
          break
        case 401:
          show('未授权，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          router.push('/login')
          break
        case 403:
          show('拒绝访问')
          break
        case 404:
          show('请求的资源不存在')
          break
        case 413:
          show('文件大小超过限制')
          break
        case 500:
          show('服务器错误')
          break
        default:
          show(msg || '未知错误')
      }
    } else if (error.request) {
      ElMessage({ type: 'error', message: '网络错误，请检查您的网络连接', duration: 2500 })
    } else {
      ElMessage({ type: 'error', message: '请求配置错误', duration: 2500 })
    }
    return Promise.reject(error)
  }
)

export default service as RequestInstance
