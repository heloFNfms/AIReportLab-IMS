<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h1>注册账号</h1>
        <p>创建您的 AIReportLab IMS 账号</p>
      </div>
      
      <div class="theme-toggle">
        <el-switch v-model="isDark" inline-prompt active-text="暗色" inactive-text="明亮" />
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
            placeholder="请输入用户名（3-50个字符）"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            size="large"
            clearable
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
            placeholder="请输入密码（至少6个字符）"
            size="large"
            show-password
            clearable
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
            placeholder="请再次输入密码"
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
            class="register-button"
            :class="{ success: successPulse }"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
        </template>
      </el-skeleton>
      
      <div class="register-footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="goToLogin">立即登录</el-link>
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
import { User, Lock, Message } from '@element-plus/icons-vue'

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
    callback(new Error('用户名只能包含字母、数字和下划线，长度为3-50个字符'))
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
  background: linear-gradient(135deg, var(--brand-gradient-start) 0%, var(--brand-gradient-end) 100%);
}

.register-box {
  width: 420px;
  padding: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-md);
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.register-header h1 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.register-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.register-form {
  margin-bottom: 20px;
}

.register-button {
  width: 100%;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.register-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.register-button.success {
  transform: scale(1.02);
  box-shadow: var(--shadow-lg);
  transition: transform 0.2s, box-shadow 0.2s;
}

.theme-toggle {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-12);
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.register-footer span {
  margin-right: 8px;
}
</style>
