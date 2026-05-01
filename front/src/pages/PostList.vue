<template>
  <div class="post-list">
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
      <el-button text @click="fetchNextPage">加载更多</el-button>
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
import { useRouter } from 'vue-router'
import { useInfiniteQuery } from '@tanstack/vue-query'
import { Loading, EditPen } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const router = useRouter()
const authStore = useAuthStore()

const { data, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam = 1 }) => getPostList({ page: pageParam, page_size: 20 }),
  getNextPageParam: (lastPage) => {
    return lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined
  },
  initialPageParam: 1,
})

const flattenPosts = computed(() => {
  return data.value?.pages.flatMap((page) => page.items) ?? []
})

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
  if (loadMoreRef.value) {
    observer.observe(loadMoreRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.post-list {
  position: relative;
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
