import request from './request'
import type { LikeParams } from './types'

export function doLike(data: LikeParams) {
  return request.post('/like/do', data)
}

export function cancelLike(data: LikeParams) {
  return request.post('/like/cancel', data)
}
