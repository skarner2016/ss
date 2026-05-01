# Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Vue 3 community frontend that connects to the existing backend API, supporting posts, comments, replies, likes, and favorites.

**Architecture:** Vue 3 + TypeScript SPA with nested Vue Router routes, Layout separation (AuthLayout for login, AppLayout for all business pages). TanStack Query manages server data with optimistic updates for likes/favorites. Pinia stores auth state (token + user info) with localStorage persistence.

**Tech Stack:** Vue 3, TypeScript, Vite, Element Plus, Vue Router 4, Pinia, TanStack Query (Vue Query), axios, md-editor-v3

**Working directory:** `front/` (relative to project root `ss/`)

---

## File Structure Summary

| File | Responsibility |
|------|----------------|
| `front/src/api/request.ts` | Axios instance, request/response interceptors |
| `front/src/api/types.ts` | All shared TS interfaces (User, Post, Comment, Reply, PageData, etc.) |
| `front/src/api/auth.ts` | Auth API functions |
| `front/src/api/post.ts` | Post API functions |
| `front/src/api/comment.ts` | Comment API functions |
| `front/src/api/reply.ts` | Reply API functions |
| `front/src/api/like.ts` | Like API functions |
| `front/src/api/favorite.ts` | Favorite API functions |
| `front/src/stores/auth.ts` | Pinia auth store |
| `front/src/composables/useAuth.ts` | Login/logout composable |
| `front/src/router/index.ts` | Vue Router config + guards |
| `front/src/layouts/AuthLayout.vue` | Centered card layout for login |
| `front/src/layouts/AppLayout.vue` | Top nav + content area layout |
| `front/src/pages/Login.vue` | Login/register page |
| `front/src/pages/PostList.vue` | Homepage post list |
| `front/src/pages/PostDetail.vue` | Post detail + comments |
| `front/src/pages/PostCreate.vue` | Create post (Markdown) |
| `front/src/pages/PostEdit.vue` | Edit post (Markdown) |
| `front/src/pages/UserProfile.vue` | User profile + posts |
| `front/src/pages/Favorites.vue` | User favorites list |
| `front/src/components/PostCard.vue` | Post card component |
| `front/src/components/CommentSection.vue` | Comments + replies section |
| `front/src/components/LikeButton.vue` | Like toggle button |
| `front/src/components/FavoriteButton.vue` | Favorite toggle button |
| `front/src/App.vue` | Root component |
| `front/src/main.ts` | App entry point |
| `front/.env` | VITE_API_BASE_URL |

---

### Task 1: Project Initialization

**Files:**
- Create: `front/` scaffold via Vite, `front/.env`, `front/src/App.vue`, `front/src/main.ts`

- [ ] **Step 1: Scaffold Vue 3 + TypeScript project**

```bash
cd /Users/skarner/workspace/skarner2016/ss
npm create vite@latest front -- --template vue-ts
cd front
```

- [ ] **Step 2: Install all dependencies**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm install vue-router@4 pinia @tanstack/vue-query axios element-plus @element-plus/icons-vue md-editor-v3 pinia-plugin-persistedstate
npm install -D @types/node unplugin-vue-components unplugin-auto-import sass
```

- [ ] **Step 3: Configure Vite**

Replace `front/vite.config.ts` with:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Configure TypeScript path alias**

Replace `front/tsconfig.json` with:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 5: Create environment file**

Create `front/.env`:

```
VITE_API_BASE_URL=/api
```

Using `/api` as baseURL since Vite proxy forwards `/api` to `http://localhost:8000/api`.

- [ ] **Step 6: Clean up scaffold**

Delete the default `front/src/components/HelloWorld.vue`, `front/src/assets/vue.svg`, and update `front/src/App.vue` and `front/src/main.ts` (will be written in later tasks).

- [ ] **Step 7: Verify dev server starts**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Expected: dev server starts on `http://localhost:3000` without errors.

- [ ] **Step 8: Commit**

```bash
git add front/
git commit -m "feat(frontend): scaffold Vue 3 + Vite project with dependencies"
```

---

### Task 2: TypeScript Types + API Layer

**Files:**
- Create: `front/src/api/types.ts`, `front/src/api/request.ts`
- Create: `front/src/api/auth.ts`, `front/src/api/post.ts`, `front/src/api/comment.ts`, `front/src/api/reply.ts`, `front/src/api/like.ts`, `front/src/api/favorite.ts`

- [ ] **Step 1: Create shared types**

Create `front/src/api/types.ts`:

```typescript
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
  title: string
  content?: string
  like_count: number
  comment_count: number
  status: number
  created_at: string
  updated_at?: string
  // Client-side fields from detail endpoint
  is_liked?: boolean
  is_favorited?: boolean
}

// Comment
export interface Comment {
  id: number
  post_id: number
  user_id: number
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
  reply_to_user_id: number | null
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
}

export interface PostCreateParams {
  title: string
  content: string
}

export interface PostUpdateParams {
  post_id: number
  title?: string
  content?: string
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
  user_id: number
  page: number
  page_size: number
}
```

- [ ] **Step 2: Create axios instance**

Create `front/src/api/request.ts`:

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import type { ApiResponse } from './types'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse
    if (res.code === 0) {
      return res.data
    }
    if (res.code === 2001) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    ElMessage.error(res.message)
    return Promise.reject(new Error(res.message))
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  },
)

export default request
```

- [ ] **Step 3: Create all API modules**

Create `front/src/api/auth.ts`:

```typescript
import request from './request'
import type { LoginParams, LoginResult, User, UpdateMeParams } from './types'

export function login(data: LoginParams) {
  return request.post<any, LoginResult>('/auth/login', data)
}

export function getMe() {
  return request.post<any, User>('/auth/me')
}

export function updateMe(data: UpdateMeParams) {
  return request.post<any, User>('/auth/update_me', data)
}
```

Create `front/src/api/post.ts`:

```typescript
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
```

Create `front/src/api/comment.ts`:

```typescript
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
```

Create `front/src/api/reply.ts`:

```typescript
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
```

Create `front/src/api/like.ts`:

```typescript
import request from './request'
import type { LikeParams } from './types'

export function doLike(data: LikeParams) {
  return request.post('/like/do', data)
}

export function cancelLike(data: LikeParams) {
  return request.post('/like/cancel', data)
}
```

Create `front/src/api/favorite.ts`:

```typescript
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
```

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npx vue-tsc --noEmit
```

Expected: No errors (or only warnings about unused imports in the generated auto-imports file).

- [ ] **Step 5: Commit**

```bash
git add front/src/api/
git commit -m "feat(frontend): add TypeScript types and API layer"
```

---

### Task 3: Pinia Auth Store + Router

**Files:**
- Create: `front/src/stores/auth.ts`, `front/src/router/index.ts`
- Modify: `front/src/main.ts`, `front/src/App.vue`

- [ ] **Step 1: Create auth store**

Create `front/src/stores/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/types'
import { login as apiLogin, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(email: string, password: string) {
    const result = await apiLogin({ email, password })
    token.value = result.token
    user.value = result.user
  }

  function logout() {
    token.value = null
    user.value = null
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      logout()
    }
  }

  return { token, user, isLoggedIn, login, logout, fetchUser }
}, {
  persist: {
    pick: ['token', 'user'],
  },
})
```

- [ ] **Step 2: Create router with guards**

Create `front/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: '',
          name: 'Login',
          component: () => import('@/pages/Login.vue'),
        },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        {
          path: '',
          name: 'PostList',
          component: () => import('@/pages/PostList.vue'),
        },
        {
          path: 'post/create',
          name: 'PostCreate',
          component: () => import('@/pages/PostCreate.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'post/:id',
          name: 'PostDetail',
          component: () => import('@/pages/PostDetail.vue'),
        },
        {
          path: 'post/:id/edit',
          name: 'PostEdit',
          component: () => import('@/pages/PostEdit.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'user/:id',
          name: 'UserProfile',
          component: () => import('@/pages/UserProfile.vue'),
        },
        {
          path: 'favorites',
          name: 'Favorites',
          component: () => import('@/pages/Favorites.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
```

- [ ] **Step 3: Create entry point and root component**

Replace `front/src/main.ts`:

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPersistedstate from 'pinia-plugin-persistedstate'
import { VueQueryPlugin } from '@tanstack/vue-query'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPersistedstate)
app.use(pinia)
app.use(router)
app.use(VueQueryPlugin)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

Replace `front/src/App.vue`:

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 4: Create placeholder pages (so router doesn't break)**

Create minimal placeholder files so the dev server starts. These will be replaced in later tasks:

Create `front/src/layouts/AuthLayout.vue`:
```vue
<template>
  <div class="auth-layout">
    <router-view />
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
</style>
```

Create `front/src/layouts/AppLayout.vue`:
```vue
<template>
  <div class="app-layout">
    <router-view />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}
</style>
```

Create `front/src/pages/Login.vue`:
```vue
<template><div>Login</div></template>
```

Create `front/src/pages/PostList.vue`:
```vue
<template><div>PostList</div></template>
```

Create `front/src/pages/PostDetail.vue`:
```vue
<template><div>PostDetail</div></template>
```

Create `front/src/pages/PostCreate.vue`:
```vue
<template><div>PostCreate</div></template>
```

Create `front/src/pages/PostEdit.vue`:
```vue
<template><div>PostEdit</div></template>
```

Create `front/src/pages/UserProfile.vue`:
```vue
<template><div>UserProfile</div></template>
```

Create `front/src/pages/Favorites.vue`:
```vue
<template><div>Favorites</div></template>
```

- [ ] **Step 5: Verify dev server starts and routes work**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Visit `http://localhost:3000/` — should see "PostList" placeholder.
Visit `http://localhost:3000/login` — should see "Login" placeholder.
Visit `http://localhost:3000/post/create` — should redirect to `/login` (requiresAuth guard).

- [ ] **Step 6: Commit**

```bash
git add front/src/stores/ front/src/router/ front/src/main.ts front/src/App.vue front/src/layouts/ front/src/pages/
git commit -m "feat(frontend): add Pinia auth store, Vue Router with guards, and placeholder pages"
```

---

### Task 4: AppLayout — Navigation Bar

**Files:**
- Modify: `front/src/layouts/AppLayout.vue`

- [ ] **Step 1: Implement full AppLayout with navigation**

Replace `front/src/layouts/AppLayout.vue`:

```vue
<template>
  <div class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">社区</router-link>
      </div>
      <div class="header-center">
        <el-menu mode="horizontal" :ellipsis="false" router :default-active="route.path">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item v-if="authStore.isLoggedIn" index="/favorites">收藏</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <template v-if="authStore.isLoggedIn">
          <el-dropdown trigger="click">
            <div class="user-avatar">
              <el-avatar :size="32" :src="authStore.user?.avatar_url || undefined">
                {{ avatarText }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push(`/user/${authStore.user?.id}`)">
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" @click="router.push('/login')">登录</el-button>
        </template>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const avatarText = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.email || ''
  return name.charAt(0).toUpperCase()
})

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left .logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  text-decoration: none;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-center .el-menu {
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.app-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }
  .app-main {
    padding: 16px 12px;
  }
}
</style>
```

- [ ] **Step 2: Verify navigation bar renders**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Visit `http://localhost:3000/` — should see navigation bar with "社区" logo, "首页" menu item, and "登录" button.

- [ ] **Step 3: Commit**

```bash
git add front/src/layouts/AppLayout.vue
git commit -m "feat(frontend): implement AppLayout with navigation bar"
```

---

### Task 5: Login Page

**Files:**
- Modify: `front/src/pages/Login.vue`

- [ ] **Step 1: Implement login page**

Replace `front/src/pages/Login.vue`:

```vue
<template>
  <el-card class="login-card">
    <h2 class="login-title">社区</h2>
    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="邮箱" size="large" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" native-type="submit" style="width: 100%">
          登录 / 注册
        </el-button>
      </el-form-item>
    </el-form>
    <p class="login-hint">首次登录将自动注册</p>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409eff;
}

.login-hint {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 0;
}
</style>
```

- [ ] **Step 2: Verify login page renders and form validates**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Visit `http://localhost:3000/login` — should see centered card with email/password inputs and "登录/注册" button. Form validation should trigger on empty submit.

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/Login.vue
git commit -m "feat(frontend): implement login page with form validation"
```

---

### Task 6: PostCard Component

**Files:**
- Create: `front/src/components/PostCard.vue`

- [ ] **Step 1: Implement PostCard**

Create `front/src/components/PostCard.vue`:

```vue
<template>
  <el-card class="post-card" shadow="hover" @click="router.push(`/post/${post.id}`)">
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-meta">
      <span class="post-author">{{ authorName }}</span>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </p>
    <div class="post-stats">
      <span class="stat-item">
        <el-icon><Star /></el-icon>
        {{ post.like_count }}
      </span>
      <span class="stat-item">
        <el-icon><ChatDotRound /></el-icon>
        {{ post.comment_count }}
      </span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, ChatDotRound } from '@element-plus/icons-vue'
import type { Post } from '@/api/types'

const props = defineProps<{
  post: Post
  authorName?: string
}>()

const router = useRouter()

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.post-card {
  cursor: pointer;
  margin-bottom: 12px;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
}

.post-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.post-meta {
  color: #909399;
  font-size: 13px;
  margin: 0 0 8px 0;
}

.post-author {
  margin-right: 12px;
}

.post-stats {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add front/src/components/PostCard.vue
git commit -m "feat(frontend): add PostCard component"
```

---

### Task 7: Home Page — Post List

**Files:**
- Modify: `front/src/pages/PostList.vue`

- [ ] **Step 1: Implement post list with infinite scroll**

Replace `front/src/pages/PostList.vue`:

```vue
<template>
  <div class="post-list">
    <div v-if="flattenPosts.length === 0 && !isLoading" class="empty-state">
      <el-empty description="暂无帖子" />
    </div>
    <PostCard
      v-for="post in flattenPosts"
      :key="post.id"
      :post="post"
    />
    <div v-if="isLoading" class="loading-more">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
    <div v-else-if="hasMore" class="load-more" ref="loadMoreRef">
      <el-button text @click="fetchNextPage">加载更多</el-button>
    </div>
    <div v-else-if="flattenPosts.length > 0" class="no-more">
      没有更多了
    </div>

    <el-button
      v-if="authStore.isLoggedIn"
      type="primary"
      circle
      class="fab-button"
      @click="router.push('/post/create')"
    >
      <el-icon><EditPen /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useInfiniteQuery } from '@tanstack/vue-query'
import { Loading, EditPen } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const router = useRouter()
const authStore = useAuthStore()

const { data, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam = 1 }) => getPostList({ page: pageParam, page_size: 20 }),
  getNextPageParam: (lastPage) => {
    return lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined
  },
  initialPageParam: 1,
})

const flattenPosts = computed(() => {
  return data.value?.pages.flatMap((page) => page.items) ?? []
})

const hasMore = computed(() => hasNextPage.value ?? false)

const loadMoreRef = ref<HTMLElement>()

// IntersectionObserver for auto-load
import { onMounted, onUnmounted } from 'vue'

let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
        fetchNextPage()
      }
    },
    { threshold: 0.1 },
  )
  if (loadMoreRef.value) {
    observer.observe(loadMoreRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.post-list {
  position: relative;
}

.loading-more, .no-more, .load-more {
  text-align: center;
  padding: 16px;
  color: #909399;
}

.fab-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 56px;
  height: 56px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
```

- [ ] **Step 2: Verify post list loads**

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Visit `http://localhost:3000/` — should see post list (or empty state if no posts exist yet). If logged in, floating "发帖" button should appear in bottom-right.

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/PostList.vue
git commit -m "feat(frontend): implement home page with post list and infinite scroll"
```

---

### Task 8: CommentSection + Reply Components

**Files:**
- Create: `front/src/components/CommentSection.vue`

- [ ] **Step 1: Implement CommentSection**

Create `front/src/components/CommentSection.vue`:

```vue
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
import { ref, reactive } from 'vue'
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

// Fetch comments
const { data: commentData, isLoading } = useQuery({
  queryKey: ['comments', props.postId],
  queryFn: () => getCommentList({ post_id: props.postId, page: 1, page_size: 20 }),
})

const comments = ref<Comment[]>([])
import { watch } from 'vue'
watch(commentData, (newData) => {
  if (newData) {
    comments.value = newData.items
    totalComments.value = newData.total
  }
})

const hasMoreComments = ref(false)

function loadMoreComments() {
  commentPage.value++
  // In a real impl, append to comments
}

// Replies map
const repliesMap = reactive<Record<number, Reply[]>>({})

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

// Delete comment
async function handleDeleteComment(commentId: number) {
  await deleteComment(commentId)
  queryClient.invalidateQueries({ queryKey: ['comments', props.postId] })
}

// Create reply
async function submitReply(commentId: number) {
  const content = replyContent[commentId]
  if (!content?.trim()) return
  await createReply({ comment_id: commentId, content })
  replyContent[commentId] = ''
  await fetchReplies(commentId)
}

// Delete reply
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
```

- [ ] **Step 2: Commit**

```bash
git add front/src/components/CommentSection.vue
git commit -m "feat(frontend): add CommentSection component with replies"
```

---

### Task 9: LikeButton + FavoriteButton

**Files:**
- Create: `front/src/components/LikeButton.vue`, `front/src/components/FavoriteButton.vue`

- [ ] **Step 1: Implement LikeButton**

Create `front/src/components/LikeButton.vue`:

```vue
<template>
  <el-button
    :type="liked ? 'primary' : 'default'"
    text
    @click="handleToggle"
  >
    <el-icon><StarFilled v-if="liked" /><Star v-else /></el-icon>
    <span style="margin-left: 4px">{{ count }}</span>
  </el-button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { doLike, cancelLike } from '@/api/like'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  targetType: number
  targetId: number
  liked: boolean
  count: number
  queryKey?: string[]
}>()

const authStore = useAuthStore()
const router = useRouter()
const queryClient = useQueryClient()

const toggleMutation = useMutation({
  mutationFn: () => {
    const params = { target_type: props.targetType, target_id: props.targetId }
    return props.liked ? cancelLike(params) : doLike(params)
  },
  onMutate: async () => {
    if (props.queryKey) {
      await queryClient.cancelQueries({ queryKey: props.queryKey })
    }
    return { previousLiked: props.liked, previousCount: props.count }
  },
  onError: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
  onSettled: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
})

function handleToggle() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  toggleMutation.mutate()
}
</script>
```

- [ ] **Step 2: Implement FavoriteButton**

Create `front/src/components/FavoriteButton.vue`:

```vue
<template>
  <el-button
    :type="favorited ? 'warning' : 'default'"
    text
    @click="handleToggle"
  >
    <el-icon><StarFilled v-if="favorited" /><Star v-else /></el-icon>
    <span style="margin-left: 4px">{{ favorited ? '已收藏' : '收藏' }}</span>
  </el-button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { doFavorite, cancelFavorite } from '@/api/favorite'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  postId: number
  favorited: boolean
  queryKey?: string[]
}>()

const authStore = useAuthStore()
const router = useRouter()
const queryClient = useQueryClient()

const toggleMutation = useMutation({
  mutationFn: () => {
    const params = { post_id: props.postId }
    return props.favorited ? cancelFavorite(params) : doFavorite(params)
  },
  onMutate: async () => {
    if (props.queryKey) {
      await queryClient.cancelQueries({ queryKey: props.queryKey })
    }
    return { previousFavorited: props.favorited }
  },
  onError: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
  onSettled: () => {
    if (props.queryKey) {
      queryClient.invalidateQueries({ queryKey: props.queryKey })
    }
  },
})

function handleToggle() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  toggleMutation.mutate()
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add front/src/components/LikeButton.vue front/src/components/FavoriteButton.vue
git commit -m "feat(frontend): add LikeButton and FavoriteButton components"
```

---

### Task 10: Post Detail Page

**Files:**
- Modify: `front/src/pages/PostDetail.vue`

- [ ] **Step 1: Implement post detail page**

Replace `front/src/pages/PostDetail.vue`:

```vue
<template>
  <div v-if="post" class="post-detail">
    <h1 class="post-title">{{ post.title }}</h1>
    <div class="post-meta">
      <router-link :to="`/user/${post.user_id}`" class="post-author">用户 #{{ post.user_id }}</router-link>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </div>
    <div class="post-content md-preview" v-html="renderedContent" />

    <div class="post-actions">
      <LikeButton
        :target-type="1"
        :target-id="post.id"
        :liked="post.is_liked ?? false"
        :count="post.like_count"
        :query-key="['post', postId]"
      />
      <FavoriteButton
        :post-id="post.id"
        :favorited="post.is_favorited ?? false"
        :query-key="['post', postId]"
      />
      <template v-if="authStore.user?.id === post.user_id">
        <el-button text @click="router.push(`/post/${postId}/edit`)">编辑</el-button>
        <el-button text type="danger" @click="handleDelete">删除</el-button>
      </template>
    </div>

    <CommentSection :post-id="post.id" />
  </div>
  <div v-else-if="isLoading" class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
    加载中...
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getPostDetail, deletePost } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import { marked } from 'marked'
import LikeButton from '@/components/LikeButton.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))

const { data: post, isLoading } = useQuery({
  queryKey: ['post', postId.value],
  queryFn: () => getPostDetail(postId.value),
})

const renderedContent = computed(() => {
  return post.value?.content ? marked.parse(post.value.content) as string : ''
})

const deleteMutation = useMutation({
  mutationFn: deletePost,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push('/')
  },
})

function handleDelete() {
  deleteMutation.mutate(postId.value)
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.post-detail {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #303133;
}

.post-meta {
  margin-bottom: 20px;
  color: #909399;
  font-size: 14px;
}

.post-author {
  color: #409eff;
  text-decoration: none;
  margin-right: 12px;
}

.post-content {
  line-height: 1.8;
  margin-bottom: 20px;
  font-size: 15px;
}

.post-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.post-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 14px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 24px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
```

- [ ] **Step 2: Verify post detail renders**

Visit `http://localhost:3000/post/1` (with a post existing in the DB). Should show title, content (markdown rendered), like/favorite buttons, and comment section.

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/PostDetail.vue
git commit -m "feat(frontend): implement post detail page with markdown rendering"
```

---

### Task 11: Post Create + Edit Pages

**Files:**
- Modify: `front/src/pages/PostCreate.vue`, `front/src/pages/PostEdit.vue`

- [ ] **Step 1: Implement PostCreate**

Replace `front/src/pages/PostCreate.vue`:

```vue
<template>
  <div class="post-create">
    <h2>发帖</h2>
    <el-form @submit.prevent="handleSubmit">
      <el-form-item>
        <el-input v-model="title" placeholder="标题" maxlength="200" show-word-limit size="large" />
      </el-form-item>
      <el-form-item>
        <MdEditor
          v-model="content"
          :style="{ height: '400px' }"
          placeholder="输入内容（支持 Markdown）..."
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit">发布</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { createPost } from '@/api/post'

const router = useRouter()
const queryClient = useQueryClient()

const title = ref('')
const content = ref('')
const loading = ref(false)

const createMutation = useMutation({
  mutationFn: createPost,
  onSuccess: (data) => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push(`/post/${data.id}`)
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await createMutation.mutateAsync({ title: title.value, content: content.value })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-create {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-create h2 {
  margin-bottom: 20px;
}
</style>
```

- [ ] **Step 2: Implement PostEdit**

Replace `front/src/pages/PostEdit.vue`:

```vue
<template>
  <div v-if="post" class="post-edit">
    <h2>编辑帖子</h2>
    <el-form @submit.prevent="handleSubmit">
      <el-form-item>
        <el-input v-model="title" placeholder="标题" maxlength="200" show-word-limit size="large" />
      </el-form-item>
      <el-form-item>
        <MdEditor
          v-model="content"
          :style="{ height: '400px' }"
          placeholder="输入内容（支持 Markdown）..."
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit">保存</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
  <div v-else class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
    加载中...
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getPostDetail, updatePost } from '@/api/post'

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))

const { data: post } = useQuery({
  queryKey: ['post', postId.value],
  queryFn: () => getPostDetail(postId.value),
})

const title = ref('')
const content = ref('')
const loading = ref(false)

// Fill form when post loads
import { watch } from 'vue'
watch(post, (p) => {
  if (p) {
    title.value = p.title
    content.value = p.content || ''
  }
}, { immediate: true })

const updateMutation = useMutation({
  mutationFn: updatePost,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['post', postId.value] })
    router.push(`/post/${postId.value}`)
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await updateMutation.mutateAsync({ post_id: postId.value, title: title.value, content: content.value })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-edit {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-edit h2 {
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/PostCreate.vue front/src/pages/PostEdit.vue
git commit -m "feat(frontend): implement post create and edit pages with Markdown editor"
```

---

### Task 12: UserProfile + Favorites Pages

**Files:**
- Modify: `front/src/pages/UserProfile.vue`, `front/src/pages/Favorites.vue`

- [ ] **Step 1: Implement UserProfile**

Replace `front/src/pages/UserProfile.vue`:

```vue
<template>
  <div v-if="user" class="user-profile">
    <el-card class="profile-card">
      <div class="profile-info">
        <el-avatar :size="64" :src="user.avatar_url || undefined">
          {{ (user.nickname || user.email).charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="profile-details">
          <h2>{{ user.nickname || '用户 #' + user.id }}</h2>
          <p v-if="user.bio" class="profile-bio">{{ user.bio }}</p>
          <p class="profile-email">{{ user.email }}</p>
          <p class="profile-time">注册于 {{ new Date(user.created_at).toLocaleDateString('zh-CN') }}</p>
        </div>
      </div>
    </el-card>

    <h3>TA 的帖子</h3>
    <PostCard v-for="post in userPosts" :key="post.id" :post="post" />
    <div v-if="userPosts.length === 0" class="empty-state">
      <el-empty description="暂无帖子" />
    </div>
  </div>
  <div v-else class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getMe } from '@/api/auth'
import { getPostList } from '@/api/post'
import PostCard from '@/components/PostCard.vue'
import type { User } from '@/api/types'

const route = useRoute()
const userId = computed(() => Number(route.params.id))

const { data: user } = useQuery({
  queryKey: ['user', userId.value],
  queryFn: () => getMe(), // Simplified: in real app, would have getUserById API
})

const { data: postData } = useQuery({
  queryKey: ['userPosts', userId.value],
  queryFn: () => getPostList({ page: 1, page_size: 50 }),
})

const userPosts = computed(() => {
  return postData.value?.items.filter((p) => p.user_id === userId.value) ?? []
})
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
}

.profile-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.profile-details h2 {
  margin: 0 0 4px 0;
}

.profile-bio {
  color: #606266;
  margin: 4px 0;
}

.profile-email, .profile-time {
  color: #909399;
  font-size: 13px;
  margin: 2px 0;
}

.empty-state {
  padding: 40px 0;
}

.loading {
  text-align: center;
  padding: 40px;
}
</style>
```

- [ ] **Step 2: Implement Favorites**

Replace `front/src/pages/Favorites.vue`:

```vue
<template>
  <div class="favorites-page">
    <h2>我的收藏</h2>
    <div v-if="favoritePosts.length === 0 && !isLoading" class="empty-state">
      <el-empty description="暂无收藏" />
    </div>
    <PostCard v-for="post in favoritePosts" :key="post.id" :post="post" />
    <div v-if="isLoading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getFavoriteList } from '@/api/favorite'
import { getPostDetail } from '@/api/post'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const authStore = useAuthStore()

const { data: favData, isLoading } = useQuery({
  queryKey: ['favorites'],
  queryFn: () => getFavoriteList({ user_id: authStore.user!.id, page: 1, page_size: 50 }),
})

// Fetch full post details for each favorite
const { data: favoritePosts } = useQuery({
  queryKey: ['favoritePosts', favData],
  queryFn: async () => {
    if (!favData.value?.items.length) return []
    const posts = await Promise.all(
      favData.value.items.map((fav) => getPostDetail(fav.post_id))
    )
    return posts
  },
  enabled: computed(() => !!favData.value?.items.length),
})
</script>

<style scoped>
.favorites-page h2 {
  margin-bottom: 20px;
}

.empty-state {
  padding: 40px 0;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/UserProfile.vue front/src/pages/Favorites.vue
git commit -m "feat(frontend): implement UserProfile and Favorites pages"
```

---

### Task 13: Final Polish + Responsive

**Files:**
- Modify: `front/src/App.vue`, `front/src/layouts/AppLayout.vue` (minor tweaks)

- [ ] **Step 1: Add global styles**

Replace `front/src/App.vue`:

```vue
<template>
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
  color: #303133;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
```

- [ ] **Step 2: Full manual test flow**

Start dev server and backend, then test:

```bash
cd /Users/skarner/workspace/skarner2016/ss/front
npm run dev
```

Test checklist:
1. Visit `/` — see post list (or empty state)
2. Click "登录" — goes to `/login`
3. Enter email + password — registers/logs in, redirects to `/`
4. Click floating "+" button — goes to `/post/create`
5. Write title + markdown content — submits, redirects to detail
6. On detail page — like button toggles, favorite button works
7. Write a comment — appears in comment section
8. Expand replies — write a reply
9. Click user name — goes to user profile
10. Navigate to "收藏" — shows favorited posts
11. Logout via dropdown — returns to logged-out state

- [ ] **Step 3: Commit**

```bash
git add front/src/App.vue
git commit -m "feat(frontend): add global styles and final polish"
```

---

## Verification

1. Start backend: `cd /Users/skarner/workspace/skarner2016/ss/backend && docker compose up -d && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd /Users/skarner/workspace/skarner2016/ss/front && npm run dev`
3. Open `http://localhost:3000` and run through full manual test flow
4. Test responsive: resize browser to < 768px width
5. Test auth guard: visit `/post/create` without login → should redirect to `/login`
6. Test token expiry: manually expire token → should redirect to `/login` on next API call
