import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import type { ApiResponse } from './types'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse
    if (res.code === 0) {
      return res.data as any
    }
    if (res.code === 2001) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    ElMessage.error(res.message)
    return Promise.reject(new Error(res.message))
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  },
)

export default request
