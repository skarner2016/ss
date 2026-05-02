<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="login-title">社区</h2>

      <!-- Step 1: Email -->
      <el-form v-if="step === 1" ref="emailFormRef" :model="emailForm" :rules="emailRules" @submit.prevent="handleSendCode">
        <el-form-item prop="email">
          <el-input v-model="emailForm.email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="sending" native-type="submit" style="width: 100%">
            发送验证码
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Step 2: Code -->
      <el-form v-else ref="codeFormRef" :model="codeForm" :rules="codeRules" @submit.prevent="handleLogin">
        <div class="code-email-hint">
          验证码已发送至 <strong>{{ emailForm.email }}</strong>
        </div>
        <el-form-item prop="code">
          <el-input v-model="codeForm.code" placeholder="6位验证码" size="large" maxlength="6" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="logging" native-type="submit" style="width: 100%">
            登录 / 注册
          </el-button>
        </el-form-item>
        <div class="resend-row">
          <span v-if="countdown > 0" class="countdown">{{ countdown }}s 后可重发</span>
          <el-button v-else text type="primary" @click="handleSendCode">重新发送</el-button>
          <el-button text @click="step = 1">更换邮箱</el-button>
        </div>
      </el-form>

      <p class="login-hint">首次登录将自动注册</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { sendCode } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const step = ref(1)
const sending = ref(false)
const logging = ref(false)
const countdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

const emailFormRef = ref<FormInstance>()
const codeFormRef = ref<FormInstance>()

const emailForm = reactive({ email: '' })
const codeForm = reactive({ code: '' })

const emailRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

const codeRules: FormRules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

function startCountdown() {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

async function handleSendCode() {
  const valid = await emailFormRef.value?.validate().catch(() => false)
  if (!valid) return

  sending.value = true
  try {
    await sendCode({ email: emailForm.email })
    step.value = 2
    startCountdown()
  } finally {
    sending.value = false
  }
}

async function handleLogin() {
  const valid = await codeFormRef.value?.validate().catch(() => false)
  if (!valid) return

  logging.value = true
  try {
    await authStore.login(emailForm.email, codeForm.code)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } finally {
    logging.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 56px);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--color-primary);
}

.code-email-hint {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.resend-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.countdown {
  color: var(--color-text-muted);
  font-size: 13px;
}

.login-hint {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 12px;
  margin-top: 0;
}
</style>
