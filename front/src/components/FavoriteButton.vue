<template>
  <el-button
    :type="favorited ? 'warning' : 'default'"
    text
    @click="handleToggle"
  >
    <el-icon><StarFilled v-if="favorited" /><Star v-else /></el-icon>
    <span style="margin-left: 4px">{{ favorited ? '已收藏' : '收藏' }}</span>
  </el-button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { doFavorite, cancelFavorite } from '@/api/favorite'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  postId: number
  favorited: boolean
  queryKey?: string[]
}>()

const authStore = useAuthStore()
const router = useRouter()
const queryClient = useQueryClient()

const toggleMutation = useMutation({
  mutationFn: () => {
    const params = { post_id: props.postId }
    return props.favorited ? cancelFavorite(params) : doFavorite(params)
  },
  onMutate: async () => {
    if (props.queryKey) {
      await queryClient.cancelQueries({ queryKey: props.queryKey })
    }
    return { previousFavorited: props.favorited }
  },
  onError: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
  onSettled: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
})

function handleToggle() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  toggleMutation.mutate()
}
</script>
