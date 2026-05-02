import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/types'
import { login as apiLogin, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(email: string, code: string) {
    const result = await apiLogin({ email, code })
    token.value = result.token
    user.value = result.user
  }

  function logout() {
    token.value = null
    user.value = null
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      logout()
    }
  }

  return { token, user, isLoggedIn, login, logout, fetchUser }
}, {
  persist: {
    pick: ['token', 'user'],
  },
})
