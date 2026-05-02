<template>
  <div v-if="user" class="user-profile">
    <div class="profile-card">
      <div class="profile-avatar">{{ avatarInitial }}</div>
      <div class="profile-details">
        <h2 class="profile-name">{{ user.nickname || '用户 #' + user.id }}</h2>
        <p v-if="user.bio" class="profile-bio">{{ user.bio }}</p>
        <div class="profile-meta">
          <span>{{ user.email }}</span>
          <span class="meta-dot">·</span>
          <span>注册于 {{ new Date(user.created_at).toLocaleDateString('zh-CN') }}</span>
        </div>
      </div>
    </div>

    <div class="section-header">TA 的帖子</div>
    <PostGrid :posts="userPosts" :query-key="['userPosts', String(userId)]" empty-text="暂无帖子" />
  </div>
  <div v-else class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getUserInfo } from '@/api/auth'
import { getPostList } from '@/api/post'
import PostGrid from '@/components/PostGrid.vue'

const route = useRoute()
const userId = computed(() => Number(route.params.id))

const { data: user } = useQuery({
  queryKey: computed(() => ['user', userId.value]),
  queryFn: () => getUserInfo(userId.value),
})

const { data: postData } = useQuery({
  queryKey: computed(() => ['userPosts', String(userId.value)]),
  queryFn: () => getPostList({ page: 1, page_size: 50, user_id: userId.value }),
})

const userPosts = computed(() => postData.value?.items ?? [])

const avatarInitial = computed(() => {
  if (!user.value) return '?'
  const name = user.value.nickname || user.value.email
  return name.charAt(0).toUpperCase()
})
</script>

<style scoped>
.user-profile {
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary-border);
  color: var(--color-primary);
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-name {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.profile-bio {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0 0 6px 0;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 12px;
}

.meta-dot {
  color: var(--color-divider);
}

.section-header {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-divider);
}

.loading {
  text-align: center;
  padding: 40px;
}
</style>
