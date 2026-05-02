<template>
  <div class="post-card" @click="router.push(`/post/${post.id}`)">
    <!-- Cover placeholder -->
    <div class="card-cover" :class="coverRatio">
      <span class="cover-icon">🖼️</span>
    </div>

    <div class="card-body">
      <p class="card-title">{{ post.title }}</p>

      <div v-if="post.channels && post.channels.length" class="card-channels" @click.stop>
        <span
          v-for="ch in post.channels"
          :key="ch.id"
          class="channel-tag"
          @click="router.push({ path: '/', query: { channel_id: ch.id } })"
        >{{ ch.name }}</span>
      </div>

      <div class="card-footer">
        <div class="card-avatar">{{ authorInitial }}</div>
        <span class="card-author">{{ post.author_nickname || '用户 #' + post.user_id }}</span>
        <div class="card-like">
          <span class="heart" :class="{ liked: post.is_liked }">♥</span>
          <span>{{ post.like_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Post } from '@/api/types'

const props = defineProps<{ post: Post }>()
const router = useRouter()

const coverRatio = computed(() => {
  const r = props.post.id % 3
  if (r === 0) return 'tall'
  if (r === 1) return 'mid'
  return 'short'
})

const authorInitial = computed(() => {
  const name = props.post.author_nickname || String(props.post.user_id)
  return name.charAt(0).toUpperCase()
})
</script>

<style scoped>
.post-card {
  background: var(--color-card);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  break-inside: avoid;
  transition: transform 0.15s, box-shadow 0.15s;
}
.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* Cover */
.card-cover {
  width: 100%;
  background: linear-gradient(135deg, #fff5f6 0%, #ffe0e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-cover.tall  { aspect-ratio: 3 / 4; }
.card-cover.mid   { aspect-ratio: 1 / 1; }
.card-cover.short { aspect-ratio: 4 / 3; }

.cover-icon {
  font-size: 24px;
  opacity: 0.25;
}

/* Body */
.card-body {
  padding: 7px 9px 9px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-bottom: 6px;
}

.channel-tag {
  font-size: 10px;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: 8px;
  padding: 1px 6px;
  cursor: pointer;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary-border);
  color: var(--color-primary);
  font-size: 9px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-author {
  font-size: 11px;
  color: var(--color-text-muted);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-like {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.heart { color: #ddd; font-size: 12px; }
.heart.liked { color: var(--color-primary); }
</style>
