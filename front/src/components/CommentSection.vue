<template>
  <div class="comment-section">
    <h3>评论 ({{ totalComments }})</h3>

    <!-- Comment input -->
    <div v-if="authStore.isLoggedIn" class="comment-input">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="2"
        placeholder="写评论..."
        maxlength="500"
        show-word-limit
      />
      <el-button type="primary" size="small" :loading="commentLoading" @click="submitComment" style="margin-top: 8px">
        发表评论
      </el-button>
    </div>
    <div v-else class="login-hint">
      <router-link to="/login">登录</router-link>后发表评论
    </div>

    <!-- Comment list -->
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div class="comment-header">
        <el-avatar :size="28">U</el-avatar>
        <span class="comment-author">{{ comment.user_nickname || '用户 #' + comment.user_id }}</span>
        <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
        <el-button
          v-if="authStore.user?.id === comment.user_id"
          text
          type="danger"
          size="small"
          @click="handleDeleteComment(comment.id)"
        >
          删除
        </el-button>
      </div>
      <div class="comment-content">{{ comment.content }}</div>

      <!-- Replies -->
      <div class="replies-section">
        <el-button text size="small" @click="toggleReplies(comment.id)">
          {{ expandedComments.has(comment.id) ? '收起' : `查看回复 (${comment.reply_count})` }}
        </el-button>

        <div v-if="expandedComments.has(comment.id)" class="replies-list">
          <div v-for="reply in repliesMap[comment.id]" :key="reply.id" class="reply-item">
            <div class="reply-header">
              <span class="reply-author">{{ reply.user_nickname || '用户 #' + reply.user_id }}</span>
              <span v-if="reply.reply_to_user_id" class="reply-to">
                回复 <span class="reply-to-user">{{ reply.reply_to_user_nickname || '用户 #' + reply.reply_to_user_id }}</span>
              </span>
              <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
              <el-button
                v-if="authStore.isLoggedIn"
                text
                size="small"
                @click="startReplyTo(comment.id, reply.user_id, reply.user_nickname)"
              >
                回复
              </el-button>
              <el-button
                v-if="authStore.user?.id === reply.user_id"
                text
                type="danger"
                size="small"
                @click="handleDeleteReply(comment.id, reply.id)"
              >
                删除
              </el-button>
            </div>
            <div class="reply-content">{{ reply.content }}</div>
          </div>

          <!-- Reply input -->
          <div v-if="authStore.isLoggedIn" class="reply-input">
            <el-input
              v-model="replyContent[comment.id]"
              size="small"
              :placeholder="replyPlaceholder[comment.id] || '写回复...'"
            />
            <el-button size="small" type="primary" @click="submitReply(comment.id)">回复</el-button>
            <el-button
              v-if="replyToUser[comment.id]"
              size="small"
              text
              @click="clearReplyTo(comment.id)"
            >
              取消
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="comments.length === 0 && !isLoading" class="empty-comments">
      暂无评论
    </div>

    <el-button
      v-if="hasMoreComments"
      text
      @click="loadMoreComments"
      :loading="isLoading"
    >
      加载更多评论
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCommentList, createComment, deleteComment } from '@/api/comment'
import { getReplyList, createReply, deleteReply } from '@/api/reply'
import { useAuthStore } from '@/stores/auth'
import type { Comment, Reply } from '@/api/types'
import { formatTime } from '@/utils/time'

const props = defineProps<{ postId: number }>()

const authStore = useAuthStore()
const queryClient = useQueryClient()

const commentPage = ref(1)
const allComments = ref<Comment[]>([])
const newComment = ref('')
const commentLoading = ref(false)
const expandedComments = reactive(new Set<number>())
const replyContent = reactive<Record<number, string>>({})
const replyToUser = reactive<Record<number, number | null>>({})
const replyPlaceholder = reactive<Record<number, string>>({})
const totalComments = ref(0)
const repliesMap = reactive<Record<number, Reply[]>>({})
const pageSize = 20

const { data: commentData, isLoading } = useQuery({
  queryKey: computed(() => ['comments', props.postId, commentPage.value]),
  queryFn: () => getCommentList({ post_id: props.postId, page: commentPage.value, page_size: pageSize }),
})

import { watch } from 'vue'
watch(commentData, (newData) => {
  if (newData) {
    if (commentPage.value === 1) {
      allComments.value = newData.items
    } else {
      allComments.value = [...allComments.value, ...newData.items]
    }
    totalComments.value = newData.total
  }
})

const comments = computed(() => allComments.value)
const hasMoreComments = computed(() => allComments.value.length < totalComments.value)

function loadMoreComments() {
  commentPage.value++
}

function toggleReplies(commentId: number) {
  if (expandedComments.has(commentId)) {
    expandedComments.delete(commentId)
  } else {
    expandedComments.add(commentId)
    if (!repliesMap[commentId]) {
      fetchReplies(commentId)
    }
  }
}

async function fetchReplies(commentId: number) {
  const data = await getReplyList({ comment_id: commentId, page: 1, page_size: 50 })
  repliesMap[commentId] = data.items
}

const createCommentMutation = useMutation({
  mutationFn: createComment,
  onSuccess: () => {
    newComment.value = ''
    commentPage.value = 1
    allComments.value = []
    queryClient.invalidateQueries({ queryKey: ['comments', props.postId] })
  },
})

async function submitComment() {
  if (!newComment.value.trim()) return
  commentLoading.value = true
  try {
    await createCommentMutation.mutateAsync({ post_id: props.postId, content: newComment.value })
  } finally {
    commentLoading.value = false
  }
}

async function handleDeleteComment(id: number) {
  try {
    await ElMessageBox.confirm('确定删除这条评论？', '提示', { type: 'warning' })
    await deleteComment(id)
    allComments.value = allComments.value.filter((c) => c.id !== id)
    totalComments.value--
  } catch (err: any) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

function startReplyTo(commentId: number, userId: number, nickname: string | null | undefined) {
  replyToUser[commentId] = userId
  replyPlaceholder[commentId] = `回复 ${nickname || '用户 #' + userId}...`
}

function clearReplyTo(commentId: number) {
  replyToUser[commentId] = null
  replyPlaceholder[commentId] = ''
}

async function submitReply(commentId: number) {
  const content = replyContent[commentId]
  if (!content?.trim()) return
  await createReply({
    comment_id: commentId,
    content,
    reply_to_user_id: replyToUser[commentId] || null,
  })
  replyContent[commentId] = ''
  replyToUser[commentId] = null
  replyPlaceholder[commentId] = ''
  await fetchReplies(commentId)
}

async function handleDeleteReply(commentId: number, replyId: number) {
  try {
    await ElMessageBox.confirm('确定删除这条回复？', '提示', { type: 'warning' })
    await deleteReply(replyId)
    await fetchReplies(commentId)
  } catch (err: any) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.comment-section {
  margin-top: 24px;
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
}

.comment-section h3 {
  margin-bottom: 16px;
}

.comment-input, .reply-input {
  margin-bottom: 16px;
}

.login-hint {
  color: #909399;
  margin-bottom: 16px;
}

.login-hint a {
  color: #409eff;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 500;
  font-size: 14px;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.replies-section {
  padding-left: 36px;
}

.reply-item {
  padding: 8px 0;
  border-top: 1px solid #f5f5f5;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-bottom: 4px;
}

.reply-author {
  font-weight: 500;
}

.reply-to {
  color: #909399;
}

.reply-to-user {
  color: #409eff;
}

.reply-time {
  color: #909399;
  font-size: 12px;
}

.reply-content {
  font-size: 13px;
  line-height: 1.5;
}

.reply-input {
  display: flex;
  gap: 8px;
  align-items: center;
}

.empty-comments {
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>
