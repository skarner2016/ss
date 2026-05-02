<template>
  <div class="favorites-page">
    <h2>我的收藏</h2>
    <div v-if="posts?.length === 0 && !isLoading" class="empty-state">
      <el-empty description="暂无收藏" />
    </div>
    <PostCard v-for="post in posts" :key="post.id" :post="post" />
    <div v-if="isLoading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getFavoriteList } from '@/api/favorite'
import PostCard from '@/components/PostCard.vue'

const { data, isLoading } = useQuery({
  queryKey: ['favorites'],
  queryFn: () => getFavoriteList({ page: 1, page_size: 50 }),
})

const posts = computed(() => data.value?.items ?? [])
</script>

<style scoped>
.favorites-page h2 {
  margin-bottom: 20px;
}

.empty-state {
  padding: 40px 0;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
