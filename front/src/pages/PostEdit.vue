<template>
  <div v-if="post" class="post-edit">
    <h2>编辑帖子</h2>
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
        <el-button type="primary" :loading="loading" native-type="submit">保存</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
  <div v-else class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
    加载中...
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getPostDetail, updatePost } from '@/api/post'
import { getPublicChannels } from '@/api/channel'

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))

const { data: post } = useQuery({
  queryKey: ['post', postId.value],
  queryFn: () => getPostDetail(postId.value),
})

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const title = ref('')
const content = ref('')
const channelIds = ref<number[]>([])
const loading = ref(false)

watch(post, (p) => {
  if (p) {
    title.value = p.title
    content.value = p.content || ''
    channelIds.value = p.channels?.map((c) => c.id) ?? []
  }
}, { immediate: true })

const updateMutation = useMutation({
  mutationFn: updatePost,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['post', postId.value] })
    router.push(`/post/${postId.value}`)
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await updateMutation.mutateAsync({
      post_id: postId.value,
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
.post-edit {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-edit h2 {
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
