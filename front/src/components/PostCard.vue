<template>
  <el-card class="post-card" shadow="hover" @click="router.push(`/post/${post.id}`)">
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-meta">
      <span class="post-author">{{ post.author_nickname || '用户 #' + post.user_id }}</span>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </p>
    <div class="post-stats" @click.stop>
      <LikeButton
        :target-id="post.id"
        :target-type="1"
        :liked="post.is_liked ?? false"
        :count="post.like_count"
        :query-key="['posts']"
      />
      <FavoriteButton
        :post-id="post.id"
        :favorited="post.is_favorited ?? false"
        :query-key="['posts']"
      />
      <span class="stat-item">
        <el-icon><ChatDotRound /></el-icon>
        {{ post.comment_count }}
      </span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import type { Post } from '@/api/types'
import { formatTime } from '@/utils/time'
import LikeButton from '@/components/LikeButton.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'

defineProps<{ post: Post }>()

const router = useRouter()
</script>

<style scoped>
.post-card {
  cursor: pointer;
  margin-bottom: 12px;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
}

.post-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.post-meta {
  color: #909399;
  font-size: 13px;
  margin: 0 0 8px 0;
  display: flex;
  gap: 12px;
}

.post-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
