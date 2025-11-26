<template>
  <div class="register-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    <div class="register-box">
      <div class="register-header">
        <div class="logo-icon">
          <el-icon :size="40"><UserFilled /></el-icon>
        </div>
        <h1>注册账号</h1>
        <p>加入 AIReportLab IMS，开启高效管理之旅</p>
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
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="用户名 (3-50字符)"
            size="large"
            class="custom-input"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="电子邮箱"
            size="large"
            class="custom-input"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="密码 (至少6位)"
            size="large"
            show-password
            class="custom-input"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
            class="custom-input"
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
            class="register-button"
            :class="{ success: successPulse }"
            @click="handleRegister"
          >
            注册账号
          </el-button>
        </el-form-item>
      </el-form>
        </template>
      </el-skeleton>
      
      <div class="register-footer">
        <span>已有账号?</span>
        <el-link type="primary" @click="goToLogin" class="login-link">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { validateEmail, validateUsername, validatePassword } from '@/utils/validator'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, Message, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const successPulse = ref(false)
const isDark = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// 验证用户名
const validateUsernameRule = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (!validateUsername(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线,长度为3-50个字符'))
  } else {
    callback()
  }
}

// 验证邮箱
const validateEmailRule = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!validateEmail(value)) {
    callback(new Error('请输入正确的邮箱格式'))
  } else {
    callback()
  }
}

// 验证密码
const validatePasswordRule = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (!validatePassword(value)) {
    callback(new Error('密码长度不能少于6个字符'))
  } else {
    callback()
  }
}

// 验证确认密码
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [{ validator: validateUsernameRule, trigger: 'blur' }],
  email: [{ validator: validateEmailRule, trigger: 'blur' }],
  password: [{ validator: validatePasswordRule, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const ok = await userStore.register(
          registerForm.username,
          registerForm.email,
          registerForm.password
        )
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

const goToLogin = () => {
  router.push('/login')
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
.register-container {
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

.register-box {
  position: relative;
  z-index: 1;
  width: 460px;
  padding: 40px;
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.6s ease-out;
}

.register-header {
  text-align: center;
  margin-bottom: 24px;
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
  transform: rotate(5deg);
  transition: transform 0.3s ease;
}

.register-box:hover .logo-icon {
  transform: rotate(0deg) scale(1.05);
}

.register-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.register-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.theme-toggle {
  position: absolute;
  top: 24px;
  right: 24px;
}

.register-form {
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

.register-button {
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

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.register-button:active {
  transform: translateY(0);
}

.register-button.success {
  animation: pulse 0.6s ease;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.register-footer span {
  margin-right: 8px;
}

.login-link {
  font-weight: 600;
  position: relative;
}

.login-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--brand-primary);
  transition: width 0.3s ease;
}

.login-link:hover::after {
  width: 100%;
}
</style>
