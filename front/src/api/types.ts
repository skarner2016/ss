// Common
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// User
export interface User {
  id: number
  email: string
  nickname: string | null
  avatar_url: string | null
  bio: string | null
  status: number
  created_at: string
}

// Post
export interface Post {
  id: number
  user_id: number
  author_nickname?: string | null
  title: string
  content?: string
  like_count: number
  comment_count: number
  status: number
  created_at: string
  updated_at?: string
  is_liked?: boolean
  is_favorited?: boolean
  channels?: Channel[]
}

// Comment
export interface Comment {
  id: number
  post_id: number
  user_id: number
  user_nickname?: string | null
  content_type: number
  content: string
  reply_count: number
  status: number
  created_at: string
}

// Reply
export interface Reply {
  id: number
  comment_id: number
  user_id: number
  user_nickname?: string | null
  reply_to_user_id: number | null
  reply_to_user_nickname?: string | null
  content_type: number
  content: string
  status: number
  created_at: string
}

// Favorite
export interface Favorite {
  id: number
  user_id: number
  post_id: number
  created_at: string
}

// Channel
export interface Channel {
  id: number
  name: string
  sort_order: number
}

// Request types
export interface LoginParams {
  email: string
  password: string
}

export interface LoginResult {
  token: string
  user: User
}

export interface UpdateMeParams {
  nickname?: string | null
  avatar_url?: string | null
  bio?: string | null
}

export interface PostListParams {
  page: number
  page_size: number
  channel_id?: number | null
}

export interface PostCreateParams {
  title: string
  content: string
  channel_ids?: number[]
}

export interface PostUpdateParams {
  post_id: number
  title?: string
  content?: string
  channel_ids?: number[] | null
}

export interface CommentCreateParams {
  post_id: number
  content: string
}

export interface CommentListParams {
  post_id: number
  page: number
  page_size: number
}

export interface ReplyCreateParams {
  comment_id: number
  content: string
  reply_to_user_id?: number | null
}

export interface ReplyListParams {
  comment_id: number
  page: number
  page_size: number
}

export interface LikeParams {
  target_type: number
  target_id: number
}

export interface FavoriteParams {
  post_id: number
}

export interface FavoriteListParams {
  page: number
  page_size: number
}
