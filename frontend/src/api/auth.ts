import request from './request'
import type { UserRegister, UserLogin, Token, User } from '@/types'

/**
 * 用户注册
 */
export const register = (data: UserRegister) => {
  return request<User>({
    url: '/auth/register',
    method: 'post',
    data,
  })
}

/**
 * 用户登录
 */
export const login = (data: UserLogin) => {
  // 使用 application/x-www-form-urlencoded 格式 (OAuth2 标准)
  const formData = new URLSearchParams()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request<Token>({
    url: '/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => {
  return request<User>({
    url: '/auth/me',
    method: 'get',
  })
}
