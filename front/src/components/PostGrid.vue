<template>
  <div>
    <div v-if="posts.length === 0 && !loading" class="empty-state">
      <el-empty :description="emptyText" />
    </div>
    <div class="waterfall">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        :query-key="queryKey"
      />
    </div>
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'
import PostCard from '@/components/PostCard.vue'
import type { Post } from '@/api/types'

defineProps<{
  posts: Post[]
  queryKey: string[]
  loading?: boolean
  emptyText?: string
}>()
</script>

<style scoped>
.waterfall {
  columns: 4;
  column-gap: 10px;
}

.empty-state {
  padding: 40px 0;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-text-muted);
}

@media (max-width: 1023px) {
  .waterfall { columns: 3; column-gap: 8px; }
}

@media (max-width: 767px) {
  .waterfall { columns: 2; column-gap: 6px; }
}
</style>
