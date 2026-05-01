import request from './request'
import type { Reply, PageData, ReplyCreateParams, ReplyListParams } from './types'

export function getReplyList(data: ReplyListParams) {
  return request.post<any, PageData<Reply>>('/reply/list', data)
}

export function createReply(data: ReplyCreateParams) {
  return request.post<any, { id: number; comment_id: number; content: string }>('/reply/create', data)
}

export function deleteReply(reply_id: number) {
  return request.post('/reply/delete', { reply_id })
}
