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
        <span class="comment-author">用户 #{{ comment.user_id }}</span>
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
              <span class="reply-author">用户 #{{ reply.user_id }}</span>
              <span v-if="reply.reply_to_user_id" class="reply-to">
                回复 <span class="reply-to-user">用户 #{{ reply.reply_to_user_id }}</span>
              </span>
              <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
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
              placeholder="写回复..."
            />
            <el-button size="small" type="primary" @click="submitReply(comment.id)">回复</el-button>
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
import { ref, reactive, watch } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { getCommentList, createComment, deleteComment } from '@/api/comment'
import { getReplyList, createReply, deleteReply } from '@/api/reply'
import { useAuthStore } from '@/stores/auth'
import type { Comment, Reply } from '@/api/types'

const props = defineProps<{ postId: number }>()

const authStore = useAuthStore()
const queryClient = useQueryClient()

const commentPage = ref(1)
const newComment = ref('')
const commentLoading = ref(false)
const expandedComments = ref(new Set<number>())
const replyContent = reactive<Record<number, string>>({})
const totalComments = ref(0)
const comments = ref<Comment[]>([])
const repliesMap = reactive<Record<number, Reply[]>>({})
const hasMoreComments = ref(false)

// Fetch comments
const { data: commentData, isLoading } = useQuery({
  queryKey: ['comments', props.postId],
  queryFn: () => getCommentList({ post_id: props.postId, page: 1, page_size: 20 }),
})

watch(commentData, (newData) => {
  if (newData) {
    comments.value = newData.items
    totalComments.value = newData.total
  }
})

function loadMoreComments() {
  commentPage.value++
}

function toggleReplies(commentId: number) {
  if (expandedComments.value.has(commentId)) {
    expandedComments.value.delete(commentId)
  } else {
    expandedComments.value.add(commentId)
    if (!repliesMap[commentId]) {
      fetchReplies(commentId)
    }
  }
}

async function fetchReplies(commentId: number) {
  const data = await getReplyList({ comment_id: commentId, page: 1, page_size: 50 })
  repliesMap[commentId] = data.items
}

// Create comment
const createCommentMutation = useMutation({
  mutationFn: createComment,
  onSuccess: () => {
    newComment.value = ''
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

async function handleDeleteComment(commentId: number) {
  await deleteComment(commentId)
  queryClient.invalidateQueries({ queryKey: ['comments', props.postId] })
}

async function submitReply(commentId: number) {
  const content = replyContent[commentId]
  if (!content?.trim()) return
  await createReply({ comment_id: commentId, content })
  replyContent[commentId] = ''
  await fetchReplies(commentId)
}

async function handleDeleteReply(commentId: number, replyId: number) {
  await deleteReply(replyId)
  await fetchReplies(commentId)
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleDateString('zh-CN')
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
