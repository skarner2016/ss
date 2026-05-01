<template>
  <div v-if="user" class="user-profile">
    <el-card class="profile-card">
      <div class="profile-info">
        <el-avatar :size="64" :src="user.avatar_url || undefined">
          {{ (user.nickname || user.email).charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="profile-details">
          <h2>{{ user.nickname || '用户 #' + user.id }}</h2>
          <p v-if="user.bio" class="profile-bio">{{ user.bio }}</p>
          <p class="profile-email">{{ user.email }}</p>
          <p class="profile-time">注册于 {{ new Date(user.created_at).toLocaleDateString('zh-CN') }}</p>
        </div>
      </div>
    </el-card>

    <h3>TA 的帖子</h3>
    <PostCard v-for="post in userPosts" :key="post.id" :post="post" />
    <div v-if="userPosts.length === 0" class="empty-state">
      <el-empty description="暂无帖子" />
    </div>
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
import { getMe } from '@/api/auth'
import { getPostList } from '@/api/post'
import PostCard from '@/components/PostCard.vue'

const route = useRoute()
const userId = computed(() => Number(route.params.id))

const { data: user } = useQuery({
  queryKey: ['user', userId.value],
  queryFn: () => getMe(),
})

const { data: postData } = useQuery({
  queryKey: ['userPosts', userId.value],
  queryFn: () => getPostList({ page: 1, page_size: 50 }),
})

const userPosts = computed(() => {
  return postData.value?.items.filter((p) => p.user_id === userId.value) ?? []
})
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
}

.profile-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.profile-details h2 {
  margin: 0 0 4px 0;
}

.profile-bio {
  color: #606266;
  margin: 4px 0;
}

.profile-email, .profile-time {
  color: #909399;
  font-size: 13px;
  margin: 2px 0;
}

.empty-state {
  padding: 40px 0;
}

.loading {
  text-align: center;
  padding: 40px;
}
</style>
