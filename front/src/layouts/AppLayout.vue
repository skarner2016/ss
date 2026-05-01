<template>
  <div class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">社区</router-link>
      </div>
      <div class="header-center">
        <el-menu mode="horizontal" :ellipsis="false" router :default-active="route.path">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item v-if="authStore.isLoggedIn" index="/favorites">收藏</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <template v-if="authStore.isLoggedIn">
          <el-dropdown trigger="click">
            <div class="user-avatar">
              <el-avatar :size="32" :src="authStore.user?.avatar_url || undefined">
                {{ avatarText }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push(`/user/${authStore.user?.id}`)">
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" @click="router.push('/login')">登录</el-button>
        </template>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const avatarText = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.email || ''
  return name.charAt(0).toUpperCase()
})

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left .logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  text-decoration: none;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-center .el-menu {
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.app-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }
  .app-main {
    padding: 16px 12px;
  }
}
</style>
