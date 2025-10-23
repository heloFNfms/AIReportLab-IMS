import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { login as loginApi, register as registerApi, getCurrentUser } from '@/api'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<User | null>(
    localStorage.getItem('userInfo') 
      ? JSON.parse(localStorage.getItem('userInfo')!) 
      : null
  )

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const res = await loginApi({ username, password })
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
      
      // 获取完整的用户信息
      try {
        const user = await getCurrentUser()
        userInfo.value = user
        localStorage.setItem('userInfo', JSON.stringify(user))
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
      
      ElMessage.success('登录成功')
      router.push('/dashboard')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    try {
      const res = await registerApi({ username, email, password })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
      return true
    } catch (error) {
      console.error('注册失败:', error)
      return false
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.push('/login')
    ElMessage.success('已退出登录')
  }

  return {
    token,
    userInfo,
    login,
    register,
    logout,
  }
})
