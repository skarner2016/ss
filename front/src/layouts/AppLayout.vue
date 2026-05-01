<template>
  <div class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">社区</router-link>
      </div>
      <div class="header-center desktop-menu">
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
          <el-button type="primary" class="desktop-login-btn" @click="router.push('/login')">登录</el-button>
        </template>
        <el-button class="hamburger" text @click="drawerVisible = true">
          <el-icon :size="22"><Menu /></el-icon>
        </el-button>
      </div>
    </el-header>

    <el-drawer v-model="drawerVisible" direction="rtl" size="240px" :show-close="false">
      <div class="drawer-menu">
        <router-link to="/" class="drawer-item" @click="drawerVisible = false">首页</router-link>
        <router-link
          v-if="authStore.isLoggedIn"
          to="/favorites"
          class="drawer-item"
          @click="drawerVisible = false"
        >
          收藏
        </router-link>
        <template v-if="authStore.isLoggedIn">
          <router-link
            :to="`/user/${authStore.user?.id}`"
            class="drawer-item"
            @click="drawerVisible = false"
          >
            个人中心
          </router-link>
          <div class="drawer-item drawer-logout" @click="handleLogout">退出登录</div>
        </template>
        <router-link
          v-else
          to="/login"
          class="drawer-item"
          @click="drawerVisible = false"
        >
          登录
        </router-link>
      </div>
    </el-drawer>

    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { Menu } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const drawerVisible = ref(false)

const avatarText = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.email || ''
  return name.charAt(0).toUpperCase()
})

function handleLogout() {
  drawerVisible.value = false
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
  gap: 8px;
}

.user-avatar {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.hamburger {
  display: none;
}

.app-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.drawer-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-item {
  display: block;
  padding: 12px 16px;
  color: #303133;
  text-decoration: none;
  border-radius: 6px;
  font-size: 15px;
  transition: background 0.15s;
}

.drawer-item:hover {
  background: #f5f7fa;
}

.drawer-logout {
  cursor: pointer;
  color: #f56c6c;
  border-top: 1px solid #e4e7ed;
  margin-top: 8px;
  padding-top: 16px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .desktop-menu,
  .desktop-login-btn {
    display: none !important;
  }

  .hamburger {
    display: inline-flex;
  }

  .app-main {
    padding: 16px 12px;
  }
}
</style>
