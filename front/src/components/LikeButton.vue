<template>
  <el-button
    :type="liked ? 'primary' : 'default'"
    text
    @click="handleToggle"
  >
    <el-icon><Pointer v-if="liked" /><Pointer v-else /></el-icon>
    <span style="margin-left: 4px">{{ count }}</span>
  </el-button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Pointer } from '@element-plus/icons-vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { doLike, cancelLike } from '@/api/like'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  targetType: number
  targetId: number
  liked: boolean
  count: number
  queryKey?: string[]
}>()

const authStore = useAuthStore()
const router = useRouter()
const queryClient = useQueryClient()

const toggleMutation = useMutation({
  mutationFn: () => {
    const params = { target_type: props.targetType, target_id: props.targetId }
    return props.liked ? cancelLike(params) : doLike(params)
  },
  onMutate: async () => {
    if (props.queryKey) {
      await queryClient.cancelQueries({ queryKey: props.queryKey })
    }
    return { previousLiked: props.liked, previousCount: props.count }
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
