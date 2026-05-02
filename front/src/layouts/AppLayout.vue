<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo">社区</router-link>

        <!-- PC: pills inline in header -->
        <div class="channel-pills desktop-pills" v-if="channels.length">
          <button
            class="pill"
            :class="{ active: selectedChannelId === 'all' }"
            @click="handleChannelSelect('all')"
          >全部</button>
          <button
            v-for="ch in channels"
            :key="ch.id"
            class="pill"
            :class="{ active: selectedChannelId === String(ch.id) }"
            @click="handleChannelSelect(String(ch.id))"
          >{{ ch.name }}</button>
        </div>

        <div class="header-actions">
          <template v-if="authStore.isLoggedIn">
            <button class="btn-publish desktop-publish" @click="router.push('/post/create')">
              ✏️ 发布
            </button>
            <el-dropdown trigger="click">
              <button class="avatar-btn">{{ avatarText }}</button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push(`/user/${authStore.user?.id}`)">
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="router.push('/favorites')">
                    我的收藏
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <button class="btn-login" @click="router.push('/login')">登录</button>
          </template>
        </div>
      </div>

      <!-- Mobile: pills below header bar -->
      <div class="channel-pills mobile-pills" v-if="channels.length">
        <button
          class="pill"
          :class="{ active: selectedChannelId === 'all' }"
          @click="handleChannelSelect('all')"
        >全部</button>
        <button
          v-for="ch in channels"
          :key="ch.id"
          class="pill"
          :class="{ active: selectedChannelId === String(ch.id) }"
          @click="handleChannelSelect(String(ch.id))"
        >{{ ch.name }}</button>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { useAuthStore } from '@/stores/auth'
import { getPublicChannels } from '@/api/channel'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const selectedChannelId = ref<string>(
  route.query.channel_id ? String(route.query.channel_id) : 'all'
)

watch(() => route.query.channel_id, (val) => {
  selectedChannelId.value = val ? String(val) : 'all'
})

function handleChannelSelect(id: string) {
  selectedChannelId.value = id
  if (id === 'all') {
    router.push({ path: '/', query: {} })
  } else {
    router.push({ path: '/', query: { channel_id: id } })
  }
}

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
  background: var(--color-card);
  box-shadow: 0 1px 0 var(--color-divider);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 56px;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
  flex-shrink: 0;
  text-decoration: none;
}

/* Pill shared styles */
.channel-pills {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}
.channel-pills::-webkit-scrollbar { display: none; }

.pill {
  flex-shrink: 0;
  padding: 5px 14px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  border: 1.5px solid var(--color-divider);
  background: var(--color-card);
  color: var(--color-text-secondary);
  transition: all 0.15s;
  font-family: inherit;
}
.pill:hover { border-color: var(--color-primary-border); color: var(--color-primary); }
.pill.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
  font-weight: 600;
}

/* Desktop pills: flex:1 in header row */
.desktop-pills {
  flex: 1;
}

/* Mobile pills: separate row below header */
.mobile-pills {
  display: none;
  padding: 6px 12px 8px;
  border-top: 1px solid var(--color-divider);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-publish {
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 18px;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.btn-login {
  background: transparent;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
  border-radius: 18px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.avatar-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  font-family: inherit;
}

.app-main {
  padding: 20px 20px;
  max-width: 1240px;
  margin: 0 auto;
}

@media (max-width: 767px) {
  .desktop-pills { display: none; }
  .mobile-pills { display: flex; }
  .desktop-publish { display: none; }
  .header-inner { padding: 0 12px; }
  .app-main { padding: 12px; }
}
</style>
