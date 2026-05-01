# 社区系统后端设计文档

## 项目概述

独立新项目，从零开始构建社区后端 API，支持发帖、评论、回复、点赞、收藏功能。

## 技术栈

| 项目 | 技术选型 |
|------|----------|
| 语言 | Python 3.12 |
| Web 框架 | FastAPI (async) |
| 数据库 | PostgreSQL |
| ORM | SQLAlchemy 2.0 (async) |
| 缓存 | Redis |
| 认证 | JWT |
| 包管理 | uv |
| 部署 | Docker Compose |

## 项目结构

```
community/
├── app/
│   ├── api/routes/
│   │   ├── auth_route.py
│   │   ├── post_route.py
│   │   ├── comment_route.py
│   │   ├── reply_route.py
│   │   ├── like_route.py
│   │   └── favorite_route.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user_model.py
│   │   ├── post_model.py
│   │   ├── comment_model.py
│   │   ├── reply_model.py
│   │   ├── like_model.py
│   │   └── favorite_model.py
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── post_schema.py
│   │   ├── comment_schema.py
│   │   ├── reply_schema.py
│   │   ├── like_schema.py
│   │   ├── favorite_schema.py
│   │   └── common_schema.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── post_service.py
│   │   ├── comment_service.py
│   │   ├── reply_service.py
│   │   ├── like_service.py
│   │   └── favorite_service.py
│   ├── core/
│   │   ├── config.py
│   │   ├── context.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   ├── security.py
│   │   ├── error_codes.py
│   │   └── exceptions.py
│   ├── main.py
│   └── utils/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── docs/superpowers/specs/schema.sql
```

## 数据库设计

详见 `docs/superpowers/specs/schema.sql`，共 6 张表：

- `users` — 用户表，邮箱登录，status 管理账号状态
- `posts` — 帖子表，含冗余 like_count/comment_count，支持软删除和审核状态
- `comments` — 一级评论表，含冗余 reply_count，支持软删除和审核状态
- `replies` — 二级回复表，记录 reply_to_user_id 用于@某人
- `likes` — 点赞表，多态设计（target_type + target_id），硬删除
- `favorites` — 收藏表，硬删除

### 字段规范

- 时间字段：`TIMESTAMPTZ`，支持 i18n，自动 UTC 存储
- 外键约束：不使用 REFERENCES，关联关系由代码保证
- 主键：`BIGSERIAL`

## API 接口设计

统一响应格式：
```json
{
    "code": 0,
    "message": "OK",
    "data": {}
}
```

所有接口使用 POST 方法，参数通过 JSON body 传递。

分页参数统一在 body 中传递：
```json
{
    "page": 1,
    "page_size": 20
}
```

### 认证模块 `/api/auth/`

| 路径 | 说明 | 认证 |
|------|------|------|
| `/api/auth/login` | 注册/登录（合一） | 否 |
| `/api/auth/me` | 获取当前用户信息 | 是 |
| `/api/auth/update_me` | 更新个人资料 | 是 |

`/api/auth/login` 业务逻辑：
- 邮箱不存在 → 自动注册 + 登录，返回 token
- 邮箱已存在 → 校验密码，通过后登录，返回 token
- 密码错误 → 返回错误
- 账号状态异常（已注销/禁用）→ 返回错误

### 帖子模块 `/api/post/`

| 路径 | 说明 | 认证 |
|------|------|------|
| `/api/post/list` | 帖子列表（分页） | 否 |
| `/api/post/detail` | 帖子详情 | 否 |
| `/api/post/create` | 发帖 | 是 |
| `/api/post/update` | 编辑帖子 | 是 |
| `/api/post/delete` | 删除帖子（软删除） | 是 |

### 评论模块 `/api/comment/`

| 路径 | 说明 | 认证 |
|------|------|------|
| `/api/comment/list` | 评论列表（分页） | 否 |
| `/api/comment/create` | 发表评论 | 是 |
| `/api/comment/delete` | 删除评论（软删除） | 是 |

### 回复模块 `/api/reply/`

| 路径 | 说明 | 认证 |
|------|------|------|
| `/api/reply/list` | 回复列表（分页） | 否 |
| `/api/reply/create` | 发表回复 | 是 |
| `/api/reply/delete` | 删除回复（软删除） | 是 |

### 互动模块 `/api/`

| 路径 | 说明 | 认证 |
|------|------|------|
| `/api/like/do` | 点赞 | 是 |
| `/api/like/cancel` | 取消点赞 | 是 |
| `/api/favorite/do` | 收藏帖子 | 是 |
| `/api/favorite/cancel` | 取消收藏 | 是 |
| `/api/favorite/list` | 用户收藏列表 | 否 |

## 核心模块设计

### 上下文管理（contextvars）

使用 `contextvars` 管理请求级上下文，不使用 FastAPI Depends 依赖注入：

```python
# core/context.py
from contextvars import ContextVar

db_session_var: ContextVar[AsyncSession] = ContextVar('db_session')
current_user_var: ContextVar[Optional[UserModel]] = ContextVar('current_user', default=None)

def get_db() -> AsyncSession:
    return db_session_var.get()

def get_current_user() -> Optional[UserModel]:
    return current_user_var.get()

def require_login() -> UserModel:
    user = current_user_var.get()
    if user is None:
        raise ApiBusinessException(*ErrorCode.UNAUTHORIZED)
    return user
```

### 中间件栈（执行顺序）

1. **CORS** — 跨域处理
2. **DBSessionMiddleware** — 创建 session → 设入 `db_session_var` → 请求结束关闭 session
3. **AuthMiddleware** — 解析 Authorization header → 查用户 → 设入 `current_user_var`
4. **请求日志** — 记录耗时

### 业务逻辑关键点

- 点赞/取消、收藏/取消：先查是否存在，再决定 INSERT 或 DELETE，同时更新冗余计数
- 冗余计数更新：`UPDATE posts SET like_count = like_count + 1` 原子操作，避免竞态
- 软删除：`UPDATE ... SET deleted_at = NOW()` + 查询时加 `WHERE deleted_at IS NULL`

## 异常处理

### 统一错误码管理

```python
# core/error_codes.py
class ErrorCode:
    # 参数错误 1xxx
    PARAM_ERROR = (1001, "参数错误")
    EMAIL_FORMAT_ERROR = (1002, "邮箱格式不正确")
    PASSWORD_TOO_SHORT = (1003, "密码长度不能少于6位")

    # 认证错误 2xxx
    UNAUTHORIZED = (2001, "未登录")
    PASSWORD_ERROR = (2002, "密码错误")
    USER_DISABLED = (2003, "账号已禁用")
    USER_CANCELLED = (2004, "账号已注销")

    # 资源错误 3xxx
    POST_NOT_FOUND = (3001, "帖子不存在")
    COMMENT_NOT_FOUND = (3002, "评论不存在")
    REPLY_NOT_FOUND = (3003, "回复不存在")
    NO_PERMISSION = (3004, "无权限操作")

    # 重复操作 4xxx
    ALREADY_LIKED = (4001, "已经点过赞了")
    NOT_LIKED = (4002, "未点赞")
    ALREADY_FAVORITED = (4003, "已经收藏过了")
    NOT_FAVORITED = (4004, "未收藏")

    # 系统错误 5xxx
    SYSTEM_ERROR = (5000, "系统异常")
```

### 异常类

```python
# core/exceptions.py
class ApiBusinessException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    @classmethod
    def from_code(cls, error_code: tuple):
        return cls(code=error_code[0], message=error_code[1])
```

### 全局异常处理器

```python
@app.exception_handler(ApiBusinessException)
async def business_exception_handler(request, exc):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None}
    )

@app.exception_handler(Exception)
async def system_exception_handler(request, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "message": "系统异常", "data": None}
    )
```

使用方式：
```python
raise ApiBusinessException(*ErrorCode.PASSWORD_ERROR)
raise ApiBusinessException.from_code(ErrorCode.POST_NOT_FOUND)
```

## 开发规范

- 包管理：uv
- 部署：Docker Compose（PostgreSQL + Redis + App）
- 数据库迁移：MVP 阶段手动建表，不使用 Alembic
- 测试框架：pytest
