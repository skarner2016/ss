<template>
  <div v-if="post" class="post-detail">
    <h1 class="post-title">{{ post.title }}</h1>
    <div class="post-meta">
      <router-link :to="`/user/${post.user_id}`" class="post-author">{{ post.author_nickname || '用户 #' + post.user_id }}</router-link>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </div>
    <div v-if="post.channels && post.channels.length > 0" class="post-channels">
      <el-tag
        v-for="ch in post.channels"
        :key="ch.id"
        size="small"
        type="info"
        class="channel-tag"
        @click="router.push({ path: '/', query: { channel_id: ch.id } })"
      >{{ ch.name }}</el-tag>
    </div>
    <div class="post-content md-preview" v-html="renderedContent" />

    <div class="post-actions">
      <LikeButton
        :target-type="1"
        :target-id="post.id"
        :liked="post.is_liked ?? false"
        :count="post.like_count"
        :query-key="['post', String(postId)]"
      />
      <FavoriteButton
        :post-id="post.id"
        :favorited="post.is_favorited ?? false"
        :query-key="['post', String(postId)]"
      />
      <template v-if="authStore.user?.id === post.user_id">
        <el-button text @click="router.push(`/post/${postId}/edit`)">编辑</el-button>
        <el-button text type="danger" @click="handleDelete">删除</el-button>
      </template>
    </div>

    <CommentSection :post-id="post.id" />
  </div>
  <div v-else-if="isLoading" class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
    加载中...
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { getPostDetail, deletePost } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })
import { formatTime } from '@/utils/time'
import LikeButton from '@/components/LikeButton.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))

const { data: post, isLoading } = useQuery({
  queryKey: ['post', String(postId.value)],
  queryFn: () => getPostDetail(postId.value),
})

const renderedContent = computed(() => {
  return post.value?.content ? DOMPurify.sanitize(marked.parse(post.value.content) as string) : ''
})

const deleteMutation = useMutation({
  mutationFn: deletePost,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push('/')
  },
})

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除这篇帖子？', '提示', { type: 'warning' })
    deleteMutation.mutate(postId.value)
  } catch {}
}
</script>

<style scoped>
.post-detail {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #303133;
}

.post-meta {
  margin-bottom: 12px;
  color: #909399;
  font-size: 14px;
}

.post-author {
  color: #409eff;
  text-decoration: none;
  margin-right: 12px;
}

.post-channels {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.channel-tag {
  cursor: pointer;
}

.post-content {
  line-height: 1.8;
  margin-bottom: 20px;
  font-size: 15px;
}

.post-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.post-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 14px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 24px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
