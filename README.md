# 社区论坛

一个全栈社区论坛应用，支持帖子发布、评论回复、点赞收藏和频道分类。

## 功能

- **用户系统** — 邮箱注册/登录，首次登录自动注册，JWT 鉴权
- **帖子** — 发布/编辑/删除，Markdown 编辑器，帖子列表无限滚动
- **频道** — 帖子最多关联 3 个频道，首页按频道 Tab 筛选
- **评论与回复** — 帖子下评论，评论下二级回复，支持 @回复对象
- **点赞 / 收藏** — 帖子点赞、收藏，我的收藏页
- **个人主页** — 查看用户信息及其发布的帖子

## 技术栈

### 后端 (`backend/`)

| 技术 | 说明 |
|------|------|
| Python 3.12 | 运行时 |
| FastAPI | Web 框架，异步路由 |
| SQLAlchemy 2 (async) | ORM，AsyncSession |
| asyncpg | PostgreSQL 异步驱动 |
| PostgreSQL 16 | 主数据库 |
| Redis 7 | 缓存（预留） |
| uv | 依赖管理 |
| PyJWT | JWT 鉴权 |
| bcrypt | 密码哈希 |
| pytest + httpx | 集成测试 |

API 路由前缀 `/api`，统一响应格式 `{"code": 0, "message": "OK", "data": ...}`。

### 前端 (`front/`)

| 技术 | 说明 |
|------|------|
| Vue 3 + TypeScript | 框架 |
| Vite 8 | 构建工具 |
| Element Plus | UI 组件库 |
| Vue Router 4 | 路由，含鉴权守卫 |
| Pinia | 状态管理，持久化 token |
| TanStack Query (Vue Query) | 服务端状态，乐观更新 |
| axios | HTTP 客户端 |
| md-editor-v3 | Markdown 编辑器 |
| marked + DOMPurify | Markdown 渲染与 XSS 防护 |

## 快速启动

依赖：Docker、Docker Compose。

```bash
docker compose up -d --build
```

- 前端：http://localhost
- 后端 API：http://localhost:8000

首次启动后需建表：

```bash
docker exec -w /app ss-backend-1 /app/.venv/bin/python -c "
import asyncio
from app.models import Base
from app.core.database import engine

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init())
"
```

## 本地开发

**后端**

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

**前端**

```bash
cd front
npm install
npm run dev   # http://localhost:3000，代理 /api 到 localhost:8000
```

**测试**

```bash
cd backend
uv run pytest -v
```

## 项目结构

```
ss/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # 路由：auth, post, comment, reply, like, favorite, channel
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 请求/响应 schema
│   │   ├── services/       # 业务逻辑
│   │   ├── middleware/      # 鉴权、DB session、日志
│   │   └── core/           # 配置、异常、安全工具
│   └── tests/
├── front/
│   └── src/
│       ├── api/            # axios 封装 + 各模块 API
│       ├── pages/          # 页面组件
│       ├── components/     # 通用组件
│       ├── stores/         # Pinia store
│       ├── layouts/        # 布局组件
│       └── router/         # 路由配置
└── docker-compose.yml
```
