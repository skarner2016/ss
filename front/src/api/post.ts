import request from './request'
import type { Post, PageData, PostListParams, PostCreateParams, PostUpdateParams } from './types'

export function getPostList(data: PostListParams) {
  return request.post<any, PageData<Post>>('/post/list', data)
}

export function getPostDetail(post_id: number) {
  return request.post<any, Post>('/post/detail', { post_id })
}

export function createPost(data: PostCreateParams) {
  return request.post<any, { id: number; title: string; content: string }>('/post/create', data)
}

export function updatePost(data: PostUpdateParams) {
  return request.post<any, { id: number; title: string; content: string }>('/post/update', data)
}

export function deletePost(post_id: number) {
  return request.post('/post/delete', { post_id })
}
