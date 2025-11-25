<template>
  <div class="login-container">
  <div class="login-box">
    <div class="login-header">
      <h1>AIReportLab IMS</h1>
      <p>用户信息管理系统</p>
    </div>
    <div class="theme-toggle">
      <el-switch v-model="isDark" inline-prompt active-text="暗色" inactive-text="明亮" />
    </div>
    
    <el-skeleton :loading="loading" animated>
      <template #default>
    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      class="login-form"
      @keyup.enter="handleLogin"
    >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            :class="{ success: successPulse }"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      </template>
    </el-skeleton>
      
      <div class="login-footer">
        <span>还没有账号？</span>
        <el-link type="primary" @click="goToRegister">立即注册</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const successPulse = ref(false)
const isDark = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const ok = await userStore.login(loginForm.username, loginForm.password)
        if (ok) {
          successPulse.value = true
          setTimeout(() => { successPulse.value = false }, 600)
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

onMounted(() => {
  const theme = localStorage.getItem('theme')
  isDark.value = theme === 'dark'
  document.documentElement.classList.toggle('dark', isDark.value)
})

watch(isDark, (val) => {
  document.documentElement.classList.toggle('dark', val)
  localStorage.setItem('theme', val ? 'dark' : 'light')
})
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, var(--brand-gradient-start) 0%, var(--brand-gradient-end) 100%);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-md);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.login-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.login-button.success {
  transform: scale(1.02);
  box-shadow: var(--shadow-lg);
  transition: transform 0.2s, box-shadow 0.2s;
}

.theme-toggle {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-12);
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.login-footer span {
  margin-right: 8px;
}
</style>
