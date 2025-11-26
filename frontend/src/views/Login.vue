<template>
  <div class="login-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="40"><DataAnalysis /></el-icon>
        </div>
        <h1>AIReportLab IMS</h1>
        <p>欢迎回来，请登录您的账号</p>
      </div>
      <div class="theme-toggle">
        <el-switch
          v-model="isDark"
          inline-prompt
          style="--el-switch-on-color: var(--brand-primary); --el-switch-off-color: var(--text-tertiary)"
          active-text="暗色"
          inactive-text="明亮"
        />
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
              placeholder="用户名"
              size="large"
              class="custom-input"
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
              placeholder="密码"
              size="large"
              show-password
              class="custom-input"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox>记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码?</el-link>
          </div>

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
          <span>还没有账号?</span>
          <el-link type="primary" @click="goToRegister" class="register-link">立即注册</el-link>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, DataAnalysis } from '@element-plus/icons-vue'

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
  position: relative;
  overflow: hidden;
  background-color: var(--bg-page);
}

.background-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 10s infinite ease-in-out;
}

.shape-1 {
  top: -10%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: var(--brand-gradient-start);
  animation-delay: 0s;
}

.shape-2 {
  bottom: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: var(--brand-gradient-end);
  animation-delay: -3s;
}

.shape-3 {
  top: 40%;
  left: 40%;
  width: 300px;
  height: 300px;
  background: var(--brand-gradient-mid);
  animation-delay: -6s;
}

.login-box {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 40px;
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.6s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  border-radius: 16px;
  box-shadow: var(--shadow-glow);
  color: white;
  transform: rotate(-5deg);
  transition: transform 0.3s ease;
}

.login-box:hover .logo-icon {
  transform: rotate(0deg) scale(1.05);
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.login-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.theme-toggle {
  position: absolute;
  top: 24px;
  right: 24px;
}

.login-form {
  margin-bottom: 24px;
}

:deep(.custom-input .el-input__wrapper) {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  box-shadow: none;
  transition: all 0.3s ease;
}

:root.dark :deep(.custom-input .el-input__wrapper) {
  background: rgba(0, 0, 0, 0.2);
}

:deep(.custom-input .el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.8);
}

:root.dark :deep(.custom-input .el-input__wrapper:hover) {
  background: rgba(0, 0, 0, 0.3);
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  background: var(--bg-card);
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

:deep(.custom-input .el-input__prefix) {
  color: var(--text-tertiary);
  font-size: 18px;
}

:deep(.custom-input .el-input__wrapper.is-focus .el-input__prefix) {
  color: var(--brand-primary);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-light) 100%);
  border: none;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.login-button:active {
  transform: translateY(0);
}

.login-button.success {
  animation: pulse 0.6s ease;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.login-footer span {
  margin-right: 8px;
}

.register-link {
  font-weight: 600;
  position: relative;
}

.register-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--brand-primary);
  transition: width 0.3s ease;
}

.register-link:hover::after {
  width: 100%;
}
</style>
