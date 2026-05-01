import request from './request'
import type { Comment, PageData, CommentCreateParams, CommentListParams } from './types'

export function getCommentList(data: CommentListParams) {
  return request.post<any, PageData<Comment>>('/comment/list', data)
}

export function createComment(data: CommentCreateParams) {
  return request.post<any, { id: number; post_id: number; content: string }>('/comment/create', data)
}

export function deleteComment(comment_id: number) {
  return request.post('/comment/delete', { comment_id })
}
