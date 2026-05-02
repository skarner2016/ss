# XHS-Style UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the community forum frontend to match Xiaohongshu (XHS) visual style — waterfall grid, red primary color, image-first cards, pill channel filter.

**Architecture:** Four focused changes: (1) inject CSS variables into App.vue, (2) rewrite AppLayout.vue navigation, (3) rewrite PostCard.vue with cover placeholder, (4) rewrite PostList.vue with waterfall layout + sidebar. No backend changes. No new API fields.

**Tech Stack:** Vue 3, TypeScript, Element Plus, TanStack Query (Vue Query), CSS columns (waterfall), scoped CSS

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `front/src/App.vue` | Modify | Inject `:root` CSS color variables |
| `front/src/layouts/AppLayout.vue` | Rewrite | New nav: logo + pill channels (PC) + publish btn + avatar |
| `front/src/components/PostCard.vue` | Rewrite | Image-first card with cover placeholder, new footer layout |
| `front/src/pages/PostList.vue` | Rewrite | Waterfall container + mobile pill channel row + PC sidebar |

---

### Task 1: Inject CSS Variables into App.vue

**Files:**
- Modify: `front/src/App.vue`

- [ ] **Step 1: Replace the global style block**

Open `front/src/App.vue`. Replace the entire `<style>` block with:

```vue
<style>
:root {
  --color-primary: #ff2442;
  --color-primary-light: #fff0f2;
  --color-primary-border: #ffccd3;
  --color-bg: #f5f5f5;
  --color-card: #ffffff;
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-divider: #f0f0f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', Roboto, sans-serif;
  background: var(--color-bg);
  color: var(--color-text-primary);
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
```

- [ ] **Step 2: Verify dev server compiles without errors**

```bash
cd front && npm run build 2>&1 | tail -5
```

Expected: no TypeScript or build errors.

- [ ] **Step 3: Commit**

```bash
git add front/src/App.vue
git commit -m "style: inject CSS color variables into root"
```

---

### Task 2: Rewrite AppLayout.vue Navigation

**Files:**
- Modify: `front/src/layouts/AppLayout.vue`

The new nav is a single 56px sticky bar. On PC (≥768px): Logo | pill channels (flex:1, scrollable) | publish btn | avatar. On mobile (<768px): Logo | publish btn | avatar — pills move to a separate row below.

The channel data is fetched here (moved from PostList) so the nav owns the pill state. Channel selection is communicated via URL query param `channel_id` (same as before) — PostList reads from route, so no prop drilling needed.

- [ ] **Step 1: Replace AppLayout.vue entirely**

```vue
<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo">社区</router-link>

        <!-- PC: pills inline in header -->
        <div class="channel-pills desktop-pills" v-if="channels.length">
          <button
            class="pill"
            :class="{ active: selectedChannelId === 'all' }"
            @click="handleChannelSelect('all')"
          >全部</button>
          <button
            v-for="ch in channels"
            :key="ch.id"
            class="pill"
            :class="{ active: selectedChannelId === String(ch.id) }"
            @click="handleChannelSelect(String(ch.id))"
          >{{ ch.name }}</button>
        </div>

        <div class="header-actions">
          <template v-if="authStore.isLoggedIn">
            <button class="btn-publish desktop-publish" @click="router.push('/post/create')">
              ✏️ 发布
            </button>
            <el-dropdown trigger="click">
              <button class="avatar-btn">{{ avatarText }}</button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push(`/user/${authStore.user?.id}`)">
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="router.push('/favorites')">
                    我的收藏
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <button class="btn-login" @click="router.push('/login')">登录</button>
          </template>
        </div>
      </div>

      <!-- Mobile: pills below header bar -->
      <div class="channel-pills mobile-pills" v-if="channels.length">
        <button
          class="pill"
          :class="{ active: selectedChannelId === 'all' }"
          @click="handleChannelSelect('all')"
        >全部</button>
        <button
          v-for="ch in channels"
          :key="ch.id"
          class="pill"
          :class="{ active: selectedChannelId === String(ch.id) }"
          @click="handleChannelSelect(String(ch.id))"
        >{{ ch.name }}</button>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import { useAuthStore } from '@/stores/auth'
import { getPublicChannels } from '@/api/channel'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const selectedChannelId = ref<string>(
  route.query.channel_id ? String(route.query.channel_id) : 'all'
)

watch(() => route.query.channel_id, (val) => {
  selectedChannelId.value = val ? String(val) : 'all'
})

function handleChannelSelect(id: string) {
  selectedChannelId.value = id
  if (id === 'all') {
    router.push({ path: '/', query: {} })
  } else {
    router.push({ path: '/', query: { channel_id: id } })
  }
}

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
  background: var(--color-card);
  box-shadow: 0 1px 0 var(--color-divider);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 56px;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
  flex-shrink: 0;
  text-decoration: none;
}

/* Pill shared styles */
.channel-pills {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}
.channel-pills::-webkit-scrollbar { display: none; }

.pill {
  flex-shrink: 0;
  padding: 5px 14px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  border: 1.5px solid var(--color-divider);
  background: var(--color-card);
  color: var(--color-text-secondary);
  transition: all 0.15s;
  font-family: inherit;
}
.pill:hover { border-color: var(--color-primary-border); color: var(--color-primary); }
.pill.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
  font-weight: 600;
}

/* Desktop pills: flex:1 in header row */
.desktop-pills {
  flex: 1;
}

/* Mobile pills: separate row below header */
.mobile-pills {
  display: none;
  padding: 6px 12px 8px;
  border-top: 1px solid var(--color-divider);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-publish {
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 18px;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.btn-login {
  background: transparent;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
  border-radius: 18px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.avatar-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  font-family: inherit;
}

.app-main {
  padding: 20px 20px;
  max-width: 1240px;
  margin: 0 auto;
}

@media (max-width: 767px) {
  .desktop-pills { display: none; }
  .mobile-pills { display: flex; }
  .desktop-publish { display: none; }
  .header-inner { padding: 0 12px; }
  .app-main { padding: 12px; }
}
</style>
```

- [ ] **Step 2: Build to verify no TypeScript errors**

```bash
cd front && npm run build 2>&1 | tail -10
```

Expected: build succeeds, no errors.

- [ ] **Step 3: Commit**

```bash
git add front/src/layouts/AppLayout.vue
git commit -m "feat: rewrite nav with pill channel filter and XHS red theme"
```

---

### Task 3: Rewrite PostCard.vue

**Files:**
- Modify: `front/src/components/PostCard.vue`

Card structure: cover placeholder (aspect ratio varies by `post.id % 3`) → title (2-line clamp) → channel tags → footer (avatar + nickname + like count). LikeButton and FavoriteButton are replaced with inline like display (read-only count + heart icon) in the card — the full interactive buttons remain on PostDetail. This keeps the card compact.

> Note: The existing LikeButton/FavoriteButton in PostCard currently handle optimistic updates. The new card shows like count as read-only (like XHS feed cards). Interactive like/favorite stays on PostDetail. This simplifies the card significantly.

- [ ] **Step 1: Replace PostCard.vue entirely**

```vue
<template>
  <div class="post-card" @click="router.push(`/post/${post.id}`)">
    <!-- Cover placeholder -->
    <div class="card-cover" :class="coverRatio">
      <span class="cover-icon">🖼️</span>
    </div>

    <div class="card-body">
      <p class="card-title">{{ post.title }}</p>

      <div v-if="post.channels && post.channels.length" class="card-channels" @click.stop>
        <span
          v-for="ch in post.channels"
          :key="ch.id"
          class="channel-tag"
          @click="router.push({ path: '/', query: { channel_id: ch.id } })"
        >{{ ch.name }}</span>
      </div>

      <div class="card-footer">
        <div class="card-avatar">{{ authorInitial }}</div>
        <span class="card-author">{{ post.author_nickname || '用户 #' + post.user_id }}</span>
        <div class="card-like">
          <span class="heart" :class="{ liked: post.is_liked }">♥</span>
          <span>{{ post.like_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Post } from '@/api/types'

const props = defineProps<{ post: Post }>()
const router = useRouter()

const coverRatio = computed(() => {
  const r = props.post.id % 3
  if (r === 0) return 'tall'
  if (r === 1) return 'mid'
  return 'short'
})

const authorInitial = computed(() => {
  const name = props.post.author_nickname || String(props.post.user_id)
  return name.charAt(0).toUpperCase()
})
</script>

<style scoped>
.post-card {
  background: var(--color-card);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  break-inside: avoid;
  transition: transform 0.15s, box-shadow 0.15s;
}
.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* Cover */
.card-cover {
  width: 100%;
  background: linear-gradient(135deg, #fff5f6 0%, #ffe0e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-cover.tall  { aspect-ratio: 3 / 4; }
.card-cover.mid   { aspect-ratio: 1 / 1; }
.card-cover.short { aspect-ratio: 4 / 3; }

.cover-icon {
  font-size: 24px;
  opacity: 0.25;
}

/* Body */
.card-body {
  padding: 7px 9px 9px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-bottom: 6px;
}

.channel-tag {
  font-size: 10px;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: 8px;
  padding: 1px 6px;
  cursor: pointer;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary-border);
  color: var(--color-primary);
  font-size: 9px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-author {
  font-size: 11px;
  color: var(--color-text-muted);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-like {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.heart { color: #ddd; font-size: 12px; }
.heart.liked { color: var(--color-primary); }
</style>
```

- [ ] **Step 2: Build to verify no TypeScript errors**

```bash
cd front && npm run build 2>&1 | tail -10
```

Expected: build succeeds. Note: PostCard no longer accepts `queryKey` prop — callers that passed it (UserProfile, Favorites, PostList) will get a TypeScript warning. Fix those in the next step.

- [ ] **Step 3: Remove queryKey prop from PostCard callers**

`front/src/pages/UserProfile.vue` line 18 — remove `:query-key="..."`:
```vue
<PostCard v-for="post in userPosts" :key="post.id" :post="post" />
```

`front/src/pages/Favorites.vue` line 7 — remove `:query-key="..."`:
```vue
<PostCard v-for="post in posts" :key="post.id" :post="post" />
```

- [ ] **Step 4: Build again to confirm clean**

```bash
cd front && npm run build 2>&1 | tail -10
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add front/src/components/PostCard.vue front/src/pages/UserProfile.vue front/src/pages/Favorites.vue
git commit -m "feat: rewrite PostCard with cover placeholder and XHS card layout"
```

---

### Task 4: Rewrite PostList.vue — Waterfall + Sidebar

**Files:**
- Modify: `front/src/pages/PostList.vue`

PostList now owns only the waterfall grid and sidebar. Channel selection is handled by AppLayout (URL-driven). PostList reads `route.query.channel_id` reactively (same as before). The mobile pill row is removed from PostList — it's now in AppLayout.

Sidebar (PC ≥1024px): hot posts (top 5 by like_count from current page data) + all channels. Both are derived client-side from existing query data — no new API calls.

- [ ] **Step 1: Replace PostList.vue entirely**

```vue
<template>
  <div class="post-list-page">
    <!-- Waterfall -->
    <div class="waterfall-wrap">
      <div v-if="flattenPosts.length === 0 && !isLoading" class="empty-state">
        <el-empty description="暂无帖子" />
      </div>

      <div class="waterfall">
        <PostCard
          v-for="post in flattenPosts"
          :key="post.id"
          :post="post"
        />
      </div>

      <div v-if="isLoading" class="status-row">
        <el-icon class="is-loading"><Loading /></el-icon> 加载中...
      </div>
      <div v-else-if="hasMore" class="status-row" ref="loadMoreRef">
        <el-button text @click="fetchNextPage">加载更多</el-button>
      </div>
      <div v-else-if="flattenPosts.length > 0" class="status-row muted">
        没有更多了
      </div>
    </div>

    <!-- Sidebar (PC only) -->
    <aside class="sidebar">
      <div class="sidebar-card" v-if="hotPosts.length">
        <div class="sidebar-title">🔥 热门帖子</div>
        <div
          v-for="(post, i) in hotPosts"
          :key="post.id"
          class="hot-item"
          @click="router.push(`/post/${post.id}`)"
        >
          <span class="hot-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
          <span class="hot-text">{{ post.title }}</span>
          <span class="hot-count">{{ post.like_count }}♥</span>
        </div>
      </div>

      <div class="sidebar-card" v-if="channels.length">
        <div class="sidebar-title">📌 全部频道</div>
        <div class="sidebar-channels">
          <span
            v-for="ch in channels"
            :key="ch.id"
            class="sidebar-channel"
            @click="router.push({ path: '/', query: { channel_id: ch.id } })"
          >{{ ch.name }}</span>
        </div>
      </div>
    </aside>

    <!-- Mobile FAB -->
    <button
      v-if="authStore.isLoggedIn"
      class="fab"
      @click="router.push('/post/create')"
    >✏</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { getPublicChannels } from '@/api/channel'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeChannelId = computed<number | null>(() => {
  const v = route.query.channel_id
  return v ? Number(v) : null
})

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const { data, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: computed(() => ['posts', activeChannelId.value]),
  queryFn: ({ pageParam = 1 }) =>
    getPostList({ page: pageParam, page_size: 20, channel_id: activeChannelId.value }),
  getNextPageParam: (lastPage) =>
    lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  initialPageParam: 1,
})

const flattenPosts = computed(() => data.value?.pages.flatMap((p) => p.items) ?? [])
const hasMore = computed(() => hasNextPage.value ?? false)

const hotPosts = computed(() =>
  [...flattenPosts.value].sort((a, b) => b.like_count - a.like_count).slice(0, 5)
)

const loadMoreRef = ref<HTMLElement>()
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
  if (loadMoreRef.value) observer.observe(loadMoreRef.value)
})

onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.post-list-page {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* Waterfall container */
.waterfall-wrap { flex: 1; min-width: 0; }

.waterfall {
  columns: 4;
  column-gap: 10px;
}

/* Sidebar */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 14px 16px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 10px;
}

.hot-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--color-divider);
  cursor: pointer;
}
.hot-item:last-child { border-bottom: none; }

.hot-rank {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: #f5f5f5;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hot-rank.top { background: var(--color-primary); color: #fff; }

.hot-text {
  font-size: 12px;
  color: var(--color-text-primary);
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-count {
  font-size: 10px;
  color: var(--color-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.sidebar-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sidebar-channel {
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid var(--color-primary-border);
  cursor: pointer;
}

/* Status rows */
.status-row {
  text-align: center;
  padding: 16px;
  color: var(--color-text-muted);
}
.status-row.muted { font-size: 13px; }

/* FAB — mobile only */
.fab {
  display: none;
  position: fixed;
  bottom: 24px;
  right: 20px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  border: none;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(255, 36, 66, 0.4);
  align-items: center;
  justify-content: center;
  font-family: inherit;
}

/* Responsive */
@media (max-width: 1023px) {
  .sidebar { display: none; }
  .waterfall { columns: 3; column-gap: 8px; }
}

@media (max-width: 767px) {
  .waterfall { columns: 2; column-gap: 6px; }
  .fab { display: flex; }
}
</style>
```

- [ ] **Step 2: Build to verify no TypeScript errors**

```bash
cd front && npm run build 2>&1 | tail -10
```

Expected: build succeeds, no errors.

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/PostList.vue
git commit -m "feat: waterfall grid layout with PC sidebar and responsive breakpoints"
```

---

### Task 5: Smoke Test in Browser

- [ ] **Step 1: Start Docker services**

```bash
docker compose up -d
```

- [ ] **Step 2: Open http://localhost and verify**

Check each item:

| Item | Expected |
|------|----------|
| Nav bar | White, 56px, red logo "社区" |
| Channel pills (PC) | Inline in nav, "全部" selected red |
| Channel pills (mobile, <768px) | Below nav bar, scrollable |
| Post grid | 4 columns on PC, 3 on tablet, 2 on mobile |
| Card cover | Pink gradient placeholder with faint 🖼️ |
| Card title | 2-line clamp, 13px |
| Card footer | Avatar initial + nickname + ♥ count |
| Sidebar (PC) | Hot posts + channel list on right |
| FAB | Hidden on PC, red circle bottom-right on mobile |
| Publish button | Red pill in nav (logged in), hidden (logged out) |
| Channel filter | Clicking pill updates URL + filters posts |

- [ ] **Step 3: Commit if any minor fixes were needed**

```bash
git add -p
git commit -m "fix: post-smoke-test adjustments"
```

---

### Task 6: Final Commit and Push

- [ ] **Step 1: Verify build is clean**

```bash
cd front && npm run build 2>&1 | tail -5
```

- [ ] **Step 2: Push branch**

```bash
git push origin feat/community-full-stack
```
