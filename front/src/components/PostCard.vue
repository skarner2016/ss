<template>
  <el-card class="post-card" shadow="hover" @click="router.push(`/post/${post.id}`)">
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-meta">
      <span class="post-author">{{ authorName }}</span>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </p>
    <div class="post-stats">
      <span class="stat-item">
        <el-icon><Star /></el-icon>
        {{ post.like_count }}
      </span>
      <span class="stat-item">
        <el-icon><ChatDotRound /></el-icon>
        {{ post.comment_count }}
      </span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, ChatDotRound } from '@element-plus/icons-vue'
import type { Post } from '@/api/types'

const props = defineProps<{
  post: Post
  authorName?: string
}>()

const router = useRouter()

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
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
}

.post-author {
  margin-right: 12px;
}

.post-stats {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
