# 社区前端设计文档

## 项目概述

在 `front/` 目录开发社区 Web 前端，对接已完成的后端 API，实现完整社区 MVP。

## 技术栈

| 项目 | 技术选型 |
|------|----------|
| 语言 | TypeScript |
| 框架 | Vue 3 (Composition API) |
| 构建 | Vite |
| UI 组件库 | Element Plus |
| 路由 | Vue Router 4 |
| 状态管理 | Pinia |
| 数据请求 | TanStack Query (Vue Query) |
| HTTP 客户端 | axios |
| 编辑器 | md-editor-v3 (Markdown) |
| 目标平台 | 桌面端为主，响应式适配移动端 |

## 架构设计

### 路由架构

嵌套路由 + Layout 分离：

- `AuthLayout`：登录页独立布局，居中卡片样式
- `AppLayout`：应用主布局，顶部导航栏 + 内容区域

所有业务页面嵌套在 `AppLayout` 下，共享导航和布局结构。

### 路由表

```
/login              → AuthLayout → Login.vue
/                   → AppLayout
  /                 → PostList.vue           (公开)
  /post/create      → PostCreate.vue        (需登录)
  /post/:id         → PostDetail.vue        (公开)
  /post/:id/edit    → PostEdit.vue          (需登录)
  /user/:id         → UserProfile.vue       (公开)
  /favorites        → Favorites.vue         (需登录)
```

### 认证流程

**公开页面（无需登录可浏览）：**
- 帖子列表（首页）
- 帖子详情
- 评论列表、回复列表
- 用户主页

**需登录（未登录跳转 `/login`）：**
- 发帖、编辑帖子
- 发表评论、回复
- 点赞、收藏
- 个人中心、我的收藏

**路由守卫：**
- 需认证路由配置 `meta: { requiresAuth: true }`
- 守卫检查 Pinia 中 token 是否存在
- 无 token 时 `router.push({ path: '/login', query: { redirect: fullPath } })`
- 登录成功后读取 `route.query.redirect` 跳回原页面

**Token 过期处理：**
- axios 响应拦截器捕获 API 返回 `code === 2001`
- 清除 Pinia token + 用户信息
- 跳转 `/login`

## 目录结构

```
front/
├── src/
│   ├── api/
│   │   ├── request.ts          # axios 实例 + 拦截器
│   │   ├── auth.ts             # POST /api/auth/login, /me, /update_me
│   │   ├── post.ts             # POST /api/post/list, detail, create, update, delete
│   │   ├── comment.ts          # POST /api/comment/list, create, delete
│   │   ├── reply.ts            # POST /api/reply/list, create, delete
│   │   ├── like.ts             # POST /api/like/do, cancel
│   │   └── favorite.ts         # POST /api/favorite/do, cancel, list
│   ├── composables/
│   │   └── useAuth.ts          # 登录、登出、获取用户信息
│   ├── layouts/
│   │   ├── AuthLayout.vue      # 登录页布局：居中卡片
│   │   └── AppLayout.vue       # 应用布局：顶部导航 + 内容区
│   ├── pages/
│   │   ├── Login.vue           # 邮箱 + 密码，单按钮登录/注册
│   │   ├── PostList.vue        # 首页帖子卡片列表
│   │   ├── PostDetail.vue      # 帖子详情 + 评论区
│   │   ├── PostCreate.vue      # 发帖（标题 + Markdown）
│   │   ├── PostEdit.vue        # 编辑帖子
│   │   ├── UserProfile.vue     # 用户主页（信息 + 帖子列表）
│   │   └── Favorites.vue       # 我的收藏列表
│   ├── components/
│   │   ├── PostCard.vue        # 帖子卡片（标题、摘要、作者、时间、计数）
│   │   ├── CommentSection.vue  # 评论区（评论列表 + 回复展开 + 输入框）
│   │   ├── LikeButton.vue      # 点赞按钮（乐观更新）
│   │   └── FavoriteButton.vue  # 收藏按钮（乐观更新）
│   ├── stores/
│   │   └── auth.ts             # token + 用户信息，localStorage 持久化
│   ├── router/
│   │   └── index.ts            # 路由配置 + 守卫
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env                         # VITE_API_BASE_URL=http://localhost:8000
```

## 核心模块设计

### API 层（`api/request.ts`）

```typescript
// axios 实例配置
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
})

// 请求拦截器：注入 Bearer token
request.interceptors.request.use((config) => {
  const token = useAuthStore().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code === 0) return data
    if (code === 2001) {  // token 过期
      useAuthStore().logout()
      router.push('/login')
    }
    ElMessage.error(message)
    return Promise.reject(new ApiError(code, message))
  }
)
```

所有 API 函数返回 `Promise<T>`，调用方无需处理统一响应格式。

### 状态管理（`stores/auth.ts`）

Pinia store 仅管理客户端状态：

- `token: string | null` — JWT token
- `user: User | null` — 当前用户信息
- `isLoggedIn: boolean` — 计算属性
- `login(email, password)` — 调用 API，存 token + 用户信息
- `logout()` — 清除 token + 用户信息
- `fetchUser()` — 调用 /me 刷新用户信息

持久化：`pinia-plugin-persistedstate` 自动同步到 localStorage。

### TanStack Query 职责

所有服务端数据由 Query 管理：

- `usePostList(page)` — 帖子列表
- `usePostDetail(id)` — 帖子详情
- `useCommentList(postId, page)` — 评论列表
- `useReplyList(commentId, page)` — 回复列表
- `useFavoriteList(page)` — 收藏列表
- `useUserPosts(userId, page)` — 用户帖子

Mutation（写操作）：

- `useCreatePost()` / `useUpdatePost()` / `useDeletePost()`
- `useCreateComment()` / `useDeleteComment()`
- `useCreateReply()` / `useDeleteReply()`
- `useToggleLike()` — 乐观更新点赞状态
- `useToggleFavorite()` — 乐观更新收藏状态

### 乐观更新（点赞/收藏）

```typescript
// 点赞乐观更新示例
useMutation({
  mutationFn: doLike,
  onMutate: async (variables) => {
    await queryClient.cancelQueries({ queryKey: ['post', variables.target_id] })
    const previous = queryClient.getQueryData(['post', variables.target_id])
    queryClient.setQueryData(['post', variables.target_id], (old) => ({
      ...old,
      like_count: old.like_count + 1,
      is_liked: true,
    }))
    return { previous }
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['post', variables.target_id], context.previous)
    ElMessage.error('操作失败')
  },
})
```

## 页面设计

### Login.vue

- AuthLayout 居中卡片
- 邮箱输入框 + 密码输入框
- 单按钮"登录"（后端自动处理注册/登录）
- 表单校验：邮箱格式、密码非空
- 错误提示：密码错误、账号禁用等用 ElMessage

### AppLayout.vue

**顶部导航栏（el-menu horizontal）：**
- 左侧：Logo + "社区" 文字链接到首页
- 中间：首页、收藏（仅登录显示）
- 右侧：
  - 未登录："登录" 按钮
  - 已登录：用户头像 + el-dropdown（个人中心、退出登录）

**内容区：** `<router-view />` 带过渡动画

### PostList.vue（首页）

- 帖子卡片列表
- 每张 PostCard：标题、内容摘要（截取前 100 字）、作者昵称、发布时间、点赞数、评论数
- TanStack Query `useInfiniteQuery` 实现滚动加载
- 右下角浮动发帖按钮（仅登录显示）
- 空状态提示

### PostDetail.vue

- 帖子完整内容（Markdown 渲染）
- 作者信息 + 发布时间
- 操作栏：点赞按钮、收藏按钮（仅登录显示）
- 作者可见：编辑、删除按钮
- 下方 CommentSection 组件

### PostCreate.vue / PostEdit.vue

- 标题输入框（el-input）
- Markdown 编辑器（md-editor-v3，实时预览）
- 提交按钮
- 编辑模式：进入页面时加载帖子内容填充

### CommentSection.vue

- 评论列表（分页加载）
- 每条评论：作者头像 + 昵称、内容、时间、回复数
- 点击"回复"展开回复列表（ReplySection 内联）
- 底部评论输入框（仅登录显示）
- 删除按钮（仅评论作者可见）

### PostCard.vue

- el-card 包裹
- 标题（链接到详情）
- 内容摘要
- 底部：作者 | 时间 | 点赞数 icon | 评论数 icon
- 点击整张卡片跳转详情

### LikeButton.vue / FavoriteButton.vue

- 图标按钮 + 计数
- 已点赞/收藏时高亮
- 未登录点击跳转 /login
- TanStack Query mutation 乐观更新

### UserProfile.vue

- 用户信息卡片（头像、昵称、bio、注册时间）
- 下方用户帖子列表（复用 PostCard）

### Favorites.vue

- 收藏帖子列表（复用 PostCard）
- 分页加载

## 导航栏响应式

- 桌面端：水平导航菜单
- 移动端（< 768px）：汉堡菜单 + 侧边抽屉

## 后端 API 对接

前端所有请求使用 POST 方法，参数通过 JSON body 传递，与后端约定一致。

请求格式：
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

分页参数：
```json
{
  "page": 1,
  "page_size": 20
}
```

响应格式：
```json
{
  "code": 0,
  "message": "OK",
  "data": {}
}
```
