<template>
  <div class="post-create">
    <h2>发帖</h2>
    <el-form @submit.prevent="handleSubmit">
      <el-form-item>
        <el-input v-model="title" placeholder="标题" maxlength="200" show-word-limit size="large" />
      </el-form-item>
      <el-form-item>
        <MdEditor
          v-model="content"
          :style="{ height: '400px' }"
          placeholder="输入内容（支持 Markdown）..."
        />
      </el-form-item>
      <el-form-item label="频道">
        <el-select
          v-model="channelIds"
          multiple
          placeholder="选择频道（最多3个）"
          style="width: 100%"
        >
          <el-option
            v-for="ch in channels"
            :key="ch.id"
            :label="ch.name"
            :value="ch.id"
            :disabled="channelIds.length >= 3 && !channelIds.includes(ch.id)"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit">发布</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMutation, useQueryClient, useQuery } from '@tanstack/vue-query'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { createPost } from '@/api/post'
import { getPublicChannels } from '@/api/channel'

const router = useRouter()
const queryClient = useQueryClient()

const title = ref('')
const content = ref('')
const channelIds = ref<number[]>([])
const loading = ref(false)

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const createMutation = useMutation({
  mutationFn: createPost,
  onSuccess: (data) => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push(`/post/${data.id}`)
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await createMutation.mutateAsync({
      title: title.value,
      content: content.value,
      channel_ids: channelIds.value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-create {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-create h2 {
  margin-bottom: 20px;
}
</style>
