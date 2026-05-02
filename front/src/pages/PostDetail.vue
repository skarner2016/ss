<template>
  <div v-if="post" class="post-detail">
    <!-- Cover placeholder -->
    <div class="post-cover" :class="coverRatio">
      <span class="cover-icon">🖼️</span>
    </div>

    <div class="post-body">
      <h1 class="post-title">{{ post.title }}</h1>

      <div v-if="post.channels && post.channels.length > 0" class="post-channels">
        <span
          v-for="ch in post.channels"
          :key="ch.id"
          class="channel-tag"
          @click="router.push({ path: '/', query: { channel_id: ch.id } })"
        >{{ ch.name }}</span>
      </div>

      <div class="post-meta">
        <div class="post-author-row">
          <div class="author-avatar">{{ authorInitial }}</div>
          <router-link :to="`/user/${post.user_id}`" class="post-author">{{ post.author_nickname || '用户 #' + post.user_id }}</router-link>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
        </div>
      </div>

      <div class="post-content md-preview" v-html="renderedContent" />

      <div class="post-actions">
        <button class="action-like" :class="{ liked: post.is_liked }" @click="handleLike">
          <span class="heart">♥</span>
          <span>{{ post.like_count }}</span>
        </button>
        <button class="action-fav" :class="{ favorited: post.is_favorited }" @click="handleFavorite">
          <span>{{ post.is_favorited ? '★' : '☆' }}</span>
        </button>
        <template v-if="authStore.user?.id === post.user_id">
          <button class="action-text" @click="router.push(`/post/${postId}/edit`)">编辑</button>
          <button class="action-text danger" @click="handleDelete">删除</button>
        </template>
      </div>

      <CommentSection :post-id="post.id" />
    </div>
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
import { doLike, cancelLike } from '@/api/like'
import { doFavorite, cancelFavorite } from '@/api/favorite'
import { useAuthStore } from '@/stores/auth'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })
import { formatTime } from '@/utils/time'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))
const queryKey = computed(() => ['post', String(postId.value)])

const { data: post, isLoading } = useQuery({
  queryKey: queryKey,
  queryFn: () => getPostDetail(postId.value),
})

const coverRatio = computed(() => {
  if (!post.value) return 'mid'
  const r = post.value.id % 3
  if (r === 0) return 'tall'
  if (r === 1) return 'mid'
  return 'short'
})

const authorInitial = computed(() => {
  if (!post.value) return '?'
  const name = post.value.author_nickname || String(post.value.user_id)
  return name.charAt(0).toUpperCase()
})

const renderedContent = computed(() => {
  return post.value?.content ? DOMPurify.sanitize(marked.parse(post.value.content) as string) : ''
})

const likeMutation = useMutation({
  mutationFn: () => {
    const params = { target_type: 1, target_id: post.value!.id }
    return post.value!.is_liked ? cancelLike(params) : doLike(params)
  },
  onSettled: () => queryClient.invalidateQueries({ queryKey: queryKey.value }),
})

const favMutation = useMutation({
  mutationFn: () => {
    const params = { post_id: post.value!.id }
    return post.value!.is_favorited ? cancelFavorite(params) : doFavorite(params)
  },
  onSettled: () => queryClient.invalidateQueries({ queryKey: queryKey.value }),
})

function handleLike() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  likeMutation.mutate()
}

function handleFavorite() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  favMutation.mutate()
}

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
  background: var(--color-card);
  border-radius: 12px;
  overflow: hidden;
  max-width: 680px;
  margin: 0 auto;
}

.post-cover {
  width: 100%;
  background: linear-gradient(135deg, #fff5f6 0%, #ffe0e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.post-cover.tall  { aspect-ratio: 3 / 4; max-height: 480px; }
.post-cover.mid   { aspect-ratio: 16 / 9; }
.post-cover.short { aspect-ratio: 4 / 3; }

.cover-icon {
  font-size: 48px;
  opacity: 0.2;
}

.post-body {
  padding: 20px;
}

.post-title {
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.post-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 12px;
}

.channel-tag {
  font-size: 11px;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: 10px;
  padding: 2px 8px;
  cursor: pointer;
}

.post-meta {
  margin-bottom: 16px;
}

.post-author-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-primary-border);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.post-author {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}
.post-author:hover { text-decoration: underline; }

.post-time {
  color: var(--color-text-muted);
  font-size: 12px;
}

.post-content {
  line-height: 1.8;
  margin-bottom: 20px;
  font-size: 15px;
  color: var(--color-text-primary);
}

.post-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
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
  gap: 4px;
  padding: 12px 0;
  border-top: 1px solid var(--color-divider);
  border-bottom: 1px solid var(--color-divider);
  margin-bottom: 24px;
}

.action-like,
.action-fav {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: inherit;
  transition: color 0.15s;
}
.action-like:hover { color: var(--color-primary); }
.action-like.liked { color: var(--color-primary); }
.action-fav:hover { color: #f59e0b; }
.action-fav.favorited { color: #f59e0b; }

.heart { font-size: 12px; }

.action-fav { font-size: 12px; }

.action-text {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-muted);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: inherit;
  transition: color 0.15s;
}
.action-text:hover { color: var(--color-text-primary); }
.action-text.danger { color: #f56c6c; margin-left: 0; }
.action-text.danger:hover { color: #e03a3a; }

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-text-muted);
}
</style>
