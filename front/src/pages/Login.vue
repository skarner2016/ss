<template>
  <el-card class="login-card">
    <h2 class="login-title">社区</h2>
    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="邮箱" size="large" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" native-type="submit" style="width: 100%">
          登录 / 注册
        </el-button>
      </el-form-item>
    </el-form>
    <p class="login-hint">首次登录将自动注册</p>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409eff;
}

.login-hint {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 0;
}
</style>
