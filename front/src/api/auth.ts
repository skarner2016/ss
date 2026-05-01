import request from './request'
import type { LoginParams, LoginResult, User, UpdateMeParams } from './types'

export function login(data: LoginParams) {
  return request.post<any, LoginResult>('/auth/login', data)
}

export function getMe() {
  return request.post<any, User>('/auth/me')
}

export function getUserInfo(userId: number) {
  return request.post<any, User>('/auth/user_info', null, { params: { user_id: userId } })
}

export function updateMe(data: UpdateMeParams) {
  return request.post<any, User>('/auth/update_me', data)
}
