<template>
  <div class="favorites-page">
    <h2>我的收藏</h2>
    <PostGrid :posts="posts" :query-key="['favorites']" :loading="isLoading" empty-text="暂无收藏" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { getFavoriteList } from '@/api/favorite'
import PostGrid from '@/components/PostGrid.vue'

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
</style>

