<template>
  <div class="post-list-page">
    <!-- Waterfall -->
    <div class="waterfall-wrap">
      <PostGrid :posts="flattenPosts" :query-key="['posts']" :loading="isLoading && flattenPosts.length === 0" empty-text="暂无帖子" />

      <div v-if="isLoading && flattenPosts.length > 0" class="status-row">
        <el-icon class="is-loading"><Loading /></el-icon> 加载中...
      </div>
      <div v-else-if="hasMore" class="status-row" ref="loadMoreRef">
        <el-button text @click="() => fetchNextPage()">加载更多</el-button>
      </div>
      <div v-else-if="flattenPosts.length > 0" class="status-row muted">
        没有更多了
      </div>
    </div>

    <!-- Sidebar (PC only) -->
    <aside class="sidebar">
      <div class="sidebar-card" v-if="hotPosts.length">
        <div class="sidebar-title">🔥 热门帖子</div>
        <div
          v-for="(post, i) in hotPosts"
          :key="post.id"
          class="hot-item"
          @click="router.push(`/post/${post.id}`)"
        >
          <span class="hot-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
          <span class="hot-text">{{ post.title }}</span>
          <span class="hot-count">{{ post.like_count }}♥</span>
        </div>
      </div>

      <div class="sidebar-card" v-if="channels.length">
        <div class="sidebar-title">📌 全部频道</div>
        <div class="sidebar-channels">
          <span
            v-for="ch in channels"
            :key="ch.id"
            class="sidebar-channel"
            @click="router.push({ path: '/', query: { channel_id: ch.id } })"
          >{{ ch.name }}</span>
        </div>
      </div>
    </aside>

    <!-- Mobile FAB -->
    <button
      v-if="authStore.isLoggedIn"
      class="fab"
      @click="router.push('/post/create')"
    >✏</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { getPublicChannels } from '@/api/channel'
import { useAuthStore } from '@/stores/auth'
import PostGrid from '@/components/PostGrid.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeChannelId = computed<number | null>(() => {
  const v = route.query.channel_id
  return v ? Number(v) : null
})

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
  staleTime: 5 * 60 * 1000,
})
const channels = computed(() => channelData.value ?? [])

const { data, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: computed(() => ['posts', activeChannelId.value]),
  queryFn: ({ pageParam = 1 }) =>
    getPostList({ page: pageParam, page_size: 20, channel_id: activeChannelId.value }),
  getNextPageParam: (lastPage) =>
    lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  initialPageParam: 1,
})

const flattenPosts = computed(() => data.value?.pages.flatMap((p) => p.items) ?? [])
const hasMore = computed(() => hasNextPage.value ?? false)

const hotPosts = computed(() =>
  [...flattenPosts.value].sort((a, b) => b.like_count - a.like_count).slice(0, 5)
)

const loadMoreRef = ref<HTMLElement>()
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
        fetchNextPage()
      }
    },
    { threshold: 0.1 },
  )
  if (loadMoreRef.value) observer.observe(loadMoreRef.value)
})

onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.post-list-page {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* Waterfall container */
.waterfall-wrap { flex: 1; min-width: 0; }

/* Sidebar */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 14px 16px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 10px;
}

.hot-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--color-divider);
  cursor: pointer;
}
.hot-item:last-child { border-bottom: none; }

.hot-rank {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: #f5f5f5;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hot-rank.top { background: var(--color-primary); color: #fff; }

.hot-text {
  font-size: 12px;
  color: var(--color-text-primary);
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-count {
  font-size: 10px;
  color: var(--color-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.sidebar-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sidebar-channel {
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid var(--color-primary-border);
  cursor: pointer;
}

/* Status rows */
.status-row {
  text-align: center;
  padding: 16px;
  color: var(--color-text-muted);
}
.status-row.muted { font-size: 13px; }

/* FAB — mobile only */
.fab {
  display: none;
  position: fixed;
  bottom: 24px;
  right: 20px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  border: none;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(255, 36, 66, 0.4);
  align-items: center;
  justify-content: center;
  font-family: inherit;
}

/* Responsive */
@media (max-width: 1023px) {
  .sidebar { display: none; }
  .waterfall { columns: 3; column-gap: 8px; }
}

@media (max-width: 767px) {
  .waterfall { columns: 2; column-gap: 6px; }
  .fab { display: flex; }
}
</style>
