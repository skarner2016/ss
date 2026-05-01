import request from './request'
import type { Channel } from './types'

export function getPublicChannels(): Promise<Channel[]> {
  return request.post<any, Channel[]>('/channel/public_list', {})
}
