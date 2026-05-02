<template>
  <div class="post-list">
    <el-tabs v-model="selectedChannelId" class="channel-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane
        v-for="ch in channels"
        :key="ch.id"
        :label="ch.name"
        :name="String(ch.id)"
      />
    </el-tabs>

    <div v-if="flattenPosts.length === 0 && !isLoading" class="empty-state">
      <el-empty description="暂无帖子" />
    </div>
    <PostCard
      v-for="post in flattenPosts"
      :key="post.id"
      :post="post"
    />
    <div v-if="isLoading" class="loading-more">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
    <div v-else-if="hasMore" class="load-more" ref="loadMoreRef">
      <el-button text @click="() => fetchNextPage()">加载更多</el-button>
    </div>
    <div v-else-if="flattenPosts.length > 0" class="no-more">
      没有更多了
    </div>

    <el-button
      v-if="authStore.isLoggedIn"
      type="primary"
      circle
      class="fab-button"
      @click="router.push('/post/create')"
    >
      <el-icon><EditPen /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import { Loading, EditPen } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { getPublicChannels } from '@/api/channel'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const selectedChannelId = ref<string>(
  route.query.channel_id ? String(route.query.channel_id) : 'all'
)

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const activeChannelId = computed<number | null>(() => {
  if (selectedChannelId.value === 'all') return null
  return Number(selectedChannelId.value)
})

const { data, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: computed(() => ['posts', activeChannelId.value]),
  queryFn: ({ pageParam = 1 }) =>
    getPostList({ page: pageParam, page_size: 20, channel_id: activeChannelId.value }),
  getNextPageParam: (lastPage) =>
    lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  initialPageParam: 1,
})

function handleTabChange(name: string | number) {
  selectedChannelId.value = String(name)
  if (name === 'all') {
    router.replace({ query: {} })
  } else {
    router.replace({ query: { channel_id: name } })
  }
}

const flattenPosts = computed(() => data.value?.pages.flatMap((page) => page.items) ?? [])
const hasMore = computed(() => hasNextPage.value ?? false)
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
.post-list {
  position: relative;
}

.channel-tabs {
  margin-bottom: 12px;
}

.loading-more, .no-more, .load-more {
  text-align: center;
  padding: 16px;
  color: #909399;
}

.fab-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 56px;
  height: 56px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
