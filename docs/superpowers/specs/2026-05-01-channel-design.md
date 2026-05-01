# Channel Feature Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add channels to posts — a post can belong to up to 3 channels; users filter the post list by channel via top tabs.

**Architecture:** Independent `channels` table + `post_channels` many-to-many join table. Channel management APIs are unauthenticated (admin backend deferred). Post create/update/list/detail APIs are extended to support channels.

**Tech Stack:** Python 3.12 + FastAPI + SQLAlchemy async (backend); Vue 3 + TypeScript + Element Plus + TanStack Query (frontend).

---

## Data Models

### channels

| Field | Type | Notes |
|-------|------|-------|
| id | BIGINT PK AUTO_INCREMENT | |
| name | VARCHAR(50) UNIQUE NOT NULL | e.g. "技术", "生活" |
| description | VARCHAR(200) | nullable |
| sort_order | SMALLINT NOT NULL DEFAULT 0 | lower = higher priority |
| status | TINYINT NOT NULL DEFAULT 1 | 1=active, 0=disabled |
| created_at | DATETIME WITH TIMEZONE | |

### post_channels

| Field | Type | Notes |
|-------|------|-------|
| post_id | BIGINT NOT NULL | references posts.id |
| channel_id | BIGINT NOT NULL | references channels.id |

- Primary key: `(post_id, channel_id)`
- Index: `idx_channel_id (channel_id)` — supports querying posts by channel

### Constraint
- Max 3 channels per post, enforced in backend service layer (raises error if exceeded).

---

## Backend

### New Files
- `backend/app/models/channel_model.py` — `ChannelModel`, `PostChannelModel`
- `backend/app/schemas/channel_schema.py` — request/response schemas
- `backend/app/services/channel_service.py` — CRUD + list logic
- `backend/app/api/routes/channel_route.py` — channel endpoints

### Modified Files
- `backend/app/models/__init__.py` — export new models
- `backend/app/api/routes/__init__.py` — register channel router
- `backend/app/schemas/post_schema.py` — add `channel_ids` to create/update/list requests
- `backend/app/api/routes/post_route.py` — handle channel_ids on write; return channels on read

### Channel API Endpoints

All use `POST` method, prefix `/api/channel`.

| Route | Auth | Body | Description |
|-------|------|------|-------------|
| `/create` | none | `{name, description?, sort_order?}` | Create channel |
| `/update` | none | `{channel_id, name?, description?, sort_order?, status?}` | Update channel |
| `/delete` | none | `{channel_id}` | Delete channel (fails if posts exist in channel) |
| `/list` | none | `{page?, page_size?}` | All channels including disabled (admin use) |
| `/public_list` | none | `{}` | Active channels only, ordered by sort_order (frontend use) |

### Post API Changes

**`POST /api/post/create`**
- Request: add `channel_ids: list[int] = []` (max 3, validated)
- On create: insert rows into `post_channels`

**`POST /api/post/update`**
- Request: add `channel_ids: list[int] | None = None`
- If provided: delete existing `post_channels` rows for this post, insert new ones

**`POST /api/post/list`**
- Request: add `channel_id: int | None = None`
- If provided: filter posts via `post_channels` join
- Response: each post item includes `channels: [{id, name}]` (batch-fetched)

**`POST /api/post/detail`**
- Response: add `channels: [{id, name}]`

### Error Cases
- `channel_ids` length > 3 → `ApiBusinessException` with appropriate error code
- `channel_ids` contains non-existent channel id → `ApiBusinessException`
- Delete channel that has posts → `ApiBusinessException`

---

## Frontend

### Modified Files
- `front/src/api/types.ts` — add `Channel` interface; add `channels` field to `Post`; add `channel_id` to `PostListParams`; add `channel_ids` to `PostCreateParams`, `PostUpdateParams`
- `front/src/api/channel.ts` — new file: `getPublicChannels()`
- `front/src/pages/PostList.vue` — channel tabs + channel_id filter
- `front/src/components/PostCard.vue` — channel badges
- `front/src/pages/PostCreate.vue` — channel multi-select (max 3)
- `front/src/pages/PostEdit.vue` — channel multi-select pre-filled
- `front/src/pages/PostDetail.vue` — display channel badges

### PostList.vue — Channel Tabs
- Fetch channels via `useQuery(['channels'], getPublicChannels)`
- Render `el-tabs` at top: "全部" tab (channel_id = null) + one tab per active channel
- Active tab stored in `ref<number | null>(null)` (`selectedChannelId`)
- On tab change: reset pagination, refetch post list with new `channel_id`
- Read initial `channel_id` from `route.query.channel_id` on mount

### PostCard.vue — Channel Badges
- Display `post.channels` as small `el-tag` elements (size="small", type="info")
- Clicking a badge navigates to `/?channel_id=<id>` (pushes route query)

### PostCreate.vue / PostEdit.vue — Channel Select
- `el-select` with `multiple`, bound to `channelIds: number[]`
- Options from `getPublicChannels()` (same query as PostList)
- Limit enforced client-side: disable options when 3 already selected
- On submit: include `channel_ids` in request body

### PostDetail.vue — Channel Badges
- Same badge rendering as PostCard

---

## Error Handling

| Scenario | Backend | Frontend |
|----------|---------|----------|
| > 3 channels selected | ApiBusinessException | el-select disabled at 3; backend error shown via ElMessage |
| Invalid channel_id | ApiBusinessException | Not possible if select options come from public_list |
| Delete channel with posts | ApiBusinessException | N/A (no delete UI in frontend) |

---

## Out of Scope
- Admin frontend for channel management (deferred to admin backend)
- Channel subscription / follow
- Channel-level permissions
- Channel post count display
