import request from './request'
import type { Favorite, PageData, FavoriteParams, FavoriteListParams } from './types'

export function doFavorite(data: FavoriteParams) {
  return request.post('/favorite/do', data)
}

export function cancelFavorite(data: FavoriteParams) {
  return request.post('/favorite/cancel', data)
}

export function getFavoriteList(data: FavoriteListParams) {
  return request.post<any, PageData<Favorite>>('/favorite/list', data)
}
