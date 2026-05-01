# 社区系统后端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建社区后端 API，支持发帖、评论、回复、点赞、收藏功能

**Architecture:** Python + FastAPI 单体应用，PostgreSQL + SQLAlchemy 2.0 async，contextvars 管理请求上下文，所有接口 POST-only + JSON body

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Redis, JWT (PyJWT), bcrypt, uv, Docker Compose

---

## 文件结构

```
app/
├── api/routes/
│   ├── __init__.py
│   ├── auth_route.py
│   ├── post_route.py
│   ├── comment_route.py
│   ├── reply_route.py
│   ├── like_route.py
│   └── favorite_route.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── user_model.py
│   ├── post_model.py
│   ├── comment_model.py
│   ├── reply_model.py
│   ├── like_model.py
│   └── favorite_model.py
├── schemas/
│   ├── __init__.py
│   ├── auth_schema.py
│   ├── post_schema.py
│   ├── comment_schema.py
│   ├── reply_schema.py
│   ├── like_schema.py
│   ├── favorite_schema.py
│   └── common_schema.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── post_service.py
│   ├── comment_service.py
│   ├── reply_service.py
│   ├── like_service.py
│   └── favorite_service.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── context.py
│   ├── database.py
│   ├── redis.py
│   ├── security.py
│   ├── error_codes.py
│   └── exceptions.py
├── middleware/
│   ├── __init__.py
│   ├── db_session.py
│   ├── auth.py
│   └── logging.py
├── utils/
│   ├── __init__.py
│   └── pagination.py
├── main.py
└── __init__.py
tests/
├── __init__.py
├── conftest.py
├── test_core/
│   ├── __init__.py
│   ├── test_security.py
│   └── test_error_codes.py
├── test_services/
│   ├── __init__.py
│   └── test_auth_service.py
└── test_api/
    ├── __init__.py
    └── test_auth_api.py
```

---

## Task 1: 项目初始化

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/core/__init__.py`

- [ ] **Step 1: 初始化 uv 项目**

```bash
cd /Users/skarner/workspace/skarner2016/ss
uv init --name community --python 3.12
```

- [ ] **Step 2: 安装依赖**

```bash
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg greenlet \
    redis pydantic-settings pyjwt bcrypt httpx
uv add --dev pytest pytest-asyncio httpx
```

- [ ] **Step 3: 创建目录结构**

```bash
mkdir -p app/api/routes app/models app/schemas app/services app/core app/middleware app/utils
touch app/__init__.py app/api/__init__.py app/api/routes/__init__.py \
    app/models/__init__.py app/schemas/__init__.py app/services/__init__.py \
    app/core/__init__.py app/middleware/__init__.py app/utils/__init__.py
```

- [ ] **Step 4: 提交**

```bash
git add pyproject.toml uv.lock app/
git commit -m "init: project scaffolding with dependencies"
```

---

## Task 2: 核心模块 — 异常与错误码

**Files:**
- Create: `app/core/exceptions.py`
- Create: `app/core/error_codes.py`
- Create: `tests/__init__.py`
- Create: `tests/test_core/__init__.py`
- Create: `tests/test_core/test_error_codes.py`

- [ ] **Step 1: 写错误码测试**

```python
# tests/test_core/test_error_codes.py
from app.core.error_codes import ErrorCode
from app.core.exceptions import ApiBusinessException


def test_error_code_tuple_format():
    """每个 ErrorCode 都是 (int, str) 元组"""
    code, message = ErrorCode.PASSWORD_ERROR
    assert isinstance(code, int)
    assert isinstance(message, str)
    assert code == 2002


def test_api_business_exception_from_tuple():
    """通过元组构造异常"""
    exc = ApiBusinessException(*ErrorCode.PASSWORD_ERROR)
    assert exc.code == 2002
    assert exc.message == "密码错误"


def test_api_business_exception_from_code():
    """通过 from_code 构造异常"""
    exc = ApiBusinessException.from_code(ErrorCode.POST_NOT_FOUND)
    assert exc.code == 3001
    assert exc.message == "帖子不存在"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/test_core/test_error_codes.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.exceptions'`

- [ ] **Step 3: 实现 exceptions.py**

```python
# app/core/exceptions.py
class ApiBusinessException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    @classmethod
    def from_code(cls, error_code: tuple):
        return cls(code=error_code[0], message=error_code[1])
```

- [ ] **Step 4: 实现 error_codes.py**

```python
# app/core/error_codes.py
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

- [ ] **Step 5: 运行测试，确认通过**

```bash
uv run pytest tests/test_core/test_error_codes.py -v
```

Expected: 3 passed

- [ ] **Step 6: 提交**

```bash
git add app/core/exceptions.py app/core/error_codes.py tests/
git commit -m "feat: error codes and exception class"
```

---

## Task 3: 核心模块 — 配置

**Files:**
- Create: `app/core/config.py`
- Create: `.env`

- [ ] **Step 1: 创建配置文件**

```python
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "community"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/community"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 2: 创建 .env**

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/community
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=dev-secret-key-change-in-production
DEBUG=true
```

- [ ] **Step 3: 提交**

```bash
echo ".env" >> .gitignore
git add app/core/config.py .gitignore
git commit -m "feat: pydantic-settings config"
```

---

## Task 4: 核心模块 — 数据库连接

**Files:**
- Create: `app/core/database.py`

- [ ] **Step 1: 实现数据库连接**

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
```

- [ ] **Step 2: 提交**

```bash
git add app/core/database.py
git commit -m "feat: async database engine and session factory"
```

---

## Task 5: 核心模块 — Redis 连接

**Files:**
- Create: `app/core/redis.py`

- [ ] **Step 1: 实现 Redis 连接**

```python
# app/core/redis.py
import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> redis.Redis:
    return redis_client
```

- [ ] **Step 2: 提交**

```bash
git add app/core/redis.py
git commit -m "feat: redis client"
```

---

## Task 6: 核心模块 — Contextvars

**Files:**
- Create: `app/core/context.py`

- [ ] **Step 1: 实现 contextvars**

```python
# app/core/context.py
from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode

db_session_var: ContextVar[AsyncSession] = ContextVar('db_session')
current_user_var: ContextVar[Optional['UserModel']] = ContextVar('current_user', default=None)


def get_db() -> AsyncSession:
    return db_session_var.get()


def get_current_user():
    return current_user_var.get()


def require_login():
    user = current_user_var.get()
    if user is None:
        raise ApiBusinessException(*ErrorCode.UNAUTHORIZED)
    return user
```

- [ ] **Step 2: 提交**

```bash
git add app/core/context.py
git commit -m "feat: contextvars for request context management"
```

---

## Task 7: SQLAlchemy 模型

**Files:**
- Create: `app/models/base.py`
- Create: `app/models/user_model.py`
- Create: `app/models/post_model.py`
- Create: `app/models/comment_model.py`
- Create: `app/models/reply_model.py`
- Create: `app/models/like_model.py`
- Create: `app/models/favorite_model.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: 创建 Base**

```python
# app/models/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2: 创建 UserModel**

```python
# app/models/user_model.py
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 3: 创建 PostModel**

```python
# app/models/post_model.py
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, SmallInteger, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 4: 创建 CommentModel**

```python
# app/models/comment_model.py
from datetime import datetime
from sqlalchemy import BigInteger, Text, SmallInteger, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reply_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 5: 创建 ReplyModel**

```python
# app/models/reply_model.py
from datetime import datetime
from sqlalchemy import BigInteger, Text, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ReplyModel(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reply_to_user_id: Mapped[int | None] = mapped_column(BigInteger)
    content_type: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 6: 创建 LikeModel**

```python
# app/models/like_model.py
from datetime import datetime
from sqlalchemy import BigInteger, SmallInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class LikeModel(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint('user_id', 'target_type', 'target_id'),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    target_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 7: 创建 FavoriteModel**

```python
# app/models/favorite_model.py
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class FavoriteModel(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint('user_id', 'post_id'),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 8: 更新 models/__init__.py**

```python
# app/models/__init__.py
from app.models.base import Base
from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.reply_model import ReplyModel
from app.models.like_model import LikeModel
from app.models.favorite_model import FavoriteModel

__all__ = [
    "Base",
    "UserModel",
    "PostModel",
    "CommentModel",
    "ReplyModel",
    "LikeModel",
    "FavoriteModel",
]
```

- [ ] **Step 9: 提交**

```bash
git add app/models/
git commit -m "feat: SQLAlchemy models for all 6 tables"
```

---

## Task 8: Pydantic Schemas

**Files:**
- Create: `app/schemas/common_schema.py`
- Create: `app/schemas/auth_schema.py`
- Create: `app/schemas/post_schema.py`
- Create: `app/schemas/comment_schema.py`
- Create: `app/schemas/reply_schema.py`
- Create: `app/schemas/like_schema.py`
- Create: `app/schemas/favorite_schema.py`
- Modify: `app/schemas/__init__.py`

- [ ] **Step 1: 创建通用 schema**

```python
# app/schemas/common_schema.py
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = 0
    message: str = "OK"
    data: dict | list | None = None


class PageRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PageData(BaseModel):
    items: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
```

- [ ] **Step 2: 创建认证 schema**

```python
# app/schemas/auth_schema.py
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UpdateMeRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=500)


class UserInfo(BaseModel):
    id: int
    email: str
    nickname: str | None
    avatar_url: str | None
    bio: str | None
    status: int
    created_at: str


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
```

- [ ] **Step 3: 创建帖子 schema**

```python
# app/schemas/post_schema.py
from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(min_length=1)


class PostUpdateRequest(BaseModel):
    post_id: int
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None


class PostDeleteRequest(BaseModel):
    post_id: int


class PostListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PostDetailRequest(BaseModel):
    post_id: int


class PostInfo(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    like_count: int
    comment_count: int
    status: int
    created_at: str
    updated_at: str
```

- [ ] **Step 4: 创建评论 schema**

```python
# app/schemas/comment_schema.py
from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    post_id: int
    content: str = Field(min_length=1)


class CommentDeleteRequest(BaseModel):
    comment_id: int


class CommentListRequest(BaseModel):
    post_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CommentInfo(BaseModel):
    id: int
    post_id: int
    user_id: int
    content_type: int
    content: str
    reply_count: int
    status: int
    created_at: str
```

- [ ] **Step 5: 创建回复 schema**

```python
# app/schemas/reply_schema.py
from pydantic import BaseModel, Field


class ReplyCreateRequest(BaseModel):
    comment_id: int
    reply_to_user_id: int | None = None
    content: str = Field(min_length=1)


class ReplyDeleteRequest(BaseModel):
    reply_id: int


class ReplyListRequest(BaseModel):
    comment_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ReplyInfo(BaseModel):
    id: int
    comment_id: int
    user_id: int
    reply_to_user_id: int | None
    content_type: int
    content: str
    status: int
    created_at: str
```

- [ ] **Step 6: 创建点赞 schema**

```python
# app/schemas/like_schema.py
from pydantic import BaseModel


class LikeDoRequest(BaseModel):
    target_type: int  # 1=post, 2=comment, 3=reply
    target_id: int


class LikeCancelRequest(BaseModel):
    target_type: int
    target_id: int
```

- [ ] **Step 7: 创建收藏 schema**

```python
# app/schemas/favorite_schema.py
from pydantic import BaseModel, Field


class FavoriteDoRequest(BaseModel):
    post_id: int


class FavoriteCancelRequest(BaseModel):
    post_id: int


class FavoriteListRequest(BaseModel):
    user_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class FavoriteInfo(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: str
```

- [ ] **Step 8: 提交**

```bash
git add app/schemas/
git commit -m "feat: Pydantic schemas for all modules"
```

---

## Task 9: Security — 密码哈希 + JWT

**Files:**
- Create: `app/core/security.py`
- Create: `tests/test_core/test_security.py`

- [ ] **Step 1: 写密码哈希测试**

```python
# tests/test_core/test_security.py
from app.core.security import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    password = "test123456"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_wrong_password():
    hashed = hash_password("correct-password")
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_token():
    payload = {"user_id": 123}
    token = create_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == 123


def test_decode_invalid_token():
    result = decode_token("invalid-token")
    assert result is None
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/test_core/test_security.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.security'`

- [ ] **Step 3: 实现 security.py**

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(payload: dict) -> str:
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    data["exp"] = expire
    return jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
uv run pytest tests/test_core/test_security.py -v
```

Expected: 4 passed

- [ ] **Step 5: 提交**

```bash
git add app/core/security.py tests/test_core/test_security.py
git commit -m "feat: password hashing and JWT token security"
```

---

## Task 10: Middleware — DBSession + Auth + Logging

**Files:**
- Create: `app/middleware/__init__.py`
- Create: `app/middleware/db_session.py`
- Create: `app/middleware/auth.py`
- Create: `app/middleware/logging.py`

- [ ] **Step 1: 实现 DBSessionMiddleware**

```python
# app/middleware/db_session.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.database import async_session_factory
from app.core.context import db_session_var


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with async_session_factory() as session:
            token = db_session_var.set(session)
            try:
                response = await call_next(request)
                return response
            finally:
                db_session_var.reset(token)
                await session.close()
```

- [ ] **Step 2: 实现 AuthMiddleware**

```python
# app/middleware/auth.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import select
from app.core.context import db_session_var, current_user_var
from app.core.security import decode_token
from app.models.user_model import UserModel


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        if token:
            payload = decode_token(token)
            if payload and "user_id" in payload:
                db = db_session_var.get()
                result = await db.execute(
                    select(UserModel).where(UserModel.id == payload["user_id"])
                )
                user = result.scalar_one_or_none()
                if user and user.status == 1:
                    current_user_var.set(user)

        try:
            response = await call_next(request)
            return response
        finally:
            current_user_var.set(None)
```

- [ ] **Step 3: 实现 LoggingMiddleware**

```python
# app/middleware/logging.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("community")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
        return response
```

- [ ] **Step 4: 提交**

```bash
git add app/middleware/
git commit -m "feat: DBSession, Auth, and Logging middleware"
```

---

## Task 11: 认证模块 — Service + Route

**Files:**
- Create: `app/services/auth_service.py`
- Create: `app/api/routes/auth_route.py`
- Create: `tests/test_services/test_auth_service.py`

- [ ] **Step 1: 写 auth service 单元测试（mock DB）**

```python
# tests/test_services/__init__.py
# (empty)

# tests/test_services/test_auth_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.auth_service import AuthService
from app.core.exceptions import ApiBusinessException
from app.models.user_model import UserModel


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_register_new_user(mock_db):
    """新邮箱：自动注册"""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    token, user = await AuthService.login_or_register(mock_db, "new@test.com", "password123")
    assert isinstance(token, str)
    assert user.email == "new@test.com"
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_login_existing_user(mock_db):
    """已注册用户：登录"""
    from app.core.security import hash_password
    fake_user = UserModel(
        id=1,
        email="exist@test.com",
        password_hash=hash_password("password123"),
        nickname=None,
        avatar_url=None,
        bio=None,
        status=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_db.execute.return_value = mock_result

    token, user = await AuthService.login_or_register(mock_db, "exist@test.com", "password123")
    assert isinstance(token, str)
    assert user.id == 1


@pytest.mark.asyncio
async def test_login_wrong_password(mock_db):
    """密码错误：抛异常"""
    from app.core.security import hash_password
    fake_user = UserModel(
        id=1,
        email="exist@test.com",
        password_hash=hash_password("password123"),
        nickname=None, avatar_url=None, bio=None,
        status=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_db.execute.return_value = mock_result

    with pytest.raises(ApiBusinessException) as exc_info:
        await AuthService.login_or_register(mock_db, "exist@test.com", "wrong-password")
    assert exc_info.value.code == 2002
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/test_services/test_auth_service.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.auth_service'`

- [ ] **Step 3: 实现 auth_service.py**

```python
# app/services/auth_service.py
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.core.security import hash_password, verify_password, create_token
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class AuthService:
    @staticmethod
    async def login_or_register(db: AsyncSession, email: str, password: str) -> tuple[str, UserModel]:
        result = await db.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            # 注册
            user = UserModel(
                email=email,
                password_hash=hash_password(password),
                status=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(user)
            await db.flush()
        else:
            # 检查账号状态
            if user.status == 0:
                raise ApiBusinessException(*ErrorCode.USER_DISABLED)
            if user.status == 2:
                raise ApiBusinessException(*ErrorCode.USER_CANCELLED)
            # 校验密码
            if not verify_password(password, user.password_hash):
                raise ApiBusinessException(*ErrorCode.PASSWORD_ERROR)

        token = create_token({"user_id": user.id})
        return token, user

    @staticmethod
    async def get_user_info(db: AsyncSession, user_id: int) -> UserModel:
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise ApiBusinessException(*ErrorCode.UNAUTHORIZED)
        return user

    @staticmethod
    async def update_user_info(db: AsyncSession, user_id: int, nickname: str | None, avatar_url: str | None, bio: str | None) -> UserModel:
        user = await AuthService.get_user_info(db, user_id)
        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url
        if bio is not None:
            user.bio = bio
        user.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return user
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
uv run pytest tests/test_services/test_auth_service.py -v
```

Expected: 3 passed

- [ ] **Step 5: 创建 auth_route.py**

```python
# app/api/routes/auth_route.py
from fastapi import APIRouter
from app.schemas.auth_schema import LoginRequest, UpdateMeRequest
from app.schemas.common_schema import BaseResponse
from app.services.auth_service import AuthService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    token, user = await AuthService.login_or_register(db, req.email, req.password)
    return BaseResponse(data={
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
        }
    })


@router.post("/me")
async def me():
    user = require_login()
    return BaseResponse(data={
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
    })


@router.post("/update_me")
async def update_me(req: UpdateMeRequest):
    db = get_db()
    user = require_login()
    updated = await AuthService.update_user_info(db, user.id, req.nickname, req.avatar_url, req.bio)
    return BaseResponse(data={
        "id": updated.id,
        "email": updated.email,
        "nickname": updated.nickname,
        "avatar_url": updated.avatar_url,
        "bio": updated.bio,
        "status": updated.status,
        "created_at": updated.created_at.isoformat(),
    })
```

- [ ] **Step 6: 提交**

```bash
git add app/services/auth_service.py app/api/routes/auth_route.py tests/test_services/
git commit -m "feat: auth module — login/register, me, update_me"
```

---

## Task 12: 帖子模块 — Service + Route

**Files:**
- Create: `app/services/post_service.py`
- Create: `app/api/routes/post_route.py`

- [ ] **Step 1: 实现 post_service.py**

```python
# app/services/post_service.py
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_model import PostModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class PostService:
    @staticmethod
    async def create(db: AsyncSession, user_id: int, title: str, content: str) -> PostModel:
        post = PostModel(
            user_id=user_id,
            title=title,
            content=content,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(post)
        await db.flush()
        return post

    @staticmethod
    async def get_detail(db: AsyncSession, post_id: int) -> PostModel:
        result = await db.execute(
            select(PostModel).where(PostModel.id == post_id, PostModel.deleted_at.is_(None))
        )
        post = result.scalar_one_or_none()
        if post is None:
            raise ApiBusinessException(*ErrorCode.POST_NOT_FOUND)
        return post

    @staticmethod
    async def get_list(db: AsyncSession, page: int, page_size: int) -> tuple[list[PostModel], int]:
        total_result = await db.execute(
            select(func.count()).select_from(PostModel).where(PostModel.deleted_at.is_(None))
        )
        total = total_result.scalar()

        result = await db.execute(
            select(PostModel)
            .where(PostModel.deleted_at.is_(None))
            .order_by(PostModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def update(db: AsyncSession, user_id: int, post_id: int, title: str | None, content: str | None) -> PostModel:
        post = await PostService.get_detail(db, post_id)
        if post.user_id != user_id:
            raise ApiBusinessException(*ErrorCode.NO_PERMISSION)
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        post.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return post

    @staticmethod
    async def delete(db: AsyncSession, user_id: int, post_id: int):
        post = await PostService.get_detail(db, post_id)
        if post.user_id != user_id:
            raise ApiBusinessException(*ErrorCode.NO_PERMISSION)
        post.deleted_at = datetime.now(timezone.utc)
        await db.flush()
```

- [ ] **Step 2: 创建 post_route.py**

```python
# app/api/routes/post_route.py
from fastapi import APIRouter
from app.schemas.post_schema import (
    PostCreateRequest, PostUpdateRequest, PostDeleteRequest,
    PostListRequest, PostDetailRequest
)
from app.schemas.common_schema import BaseResponse, PageData
from app.services.post_service import PostService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/post", tags=["帖子"])


@router.post("/create")
async def create_post(req: PostCreateRequest):
    db = get_db()
    user = require_login()
    post = await PostService.create(db, user.id, req.title, req.content)
    return BaseResponse(data={
        "id": post.id,
        "title": post.title,
        "content": post.content,
    })


@router.post("/detail")
async def post_detail(req: PostDetailRequest):
    db = get_db()
    post = await PostService.get_detail(db, req.post_id)
    return BaseResponse(data={
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "status": post.status,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    })


@router.post("/list")
async def post_list(req: PostListRequest):
    db = get_db()
    posts, total = await PostService.get_list(db, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "title": p.title,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at.isoformat(),
        }
        for p in posts
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/update")
async def update_post(req: PostUpdateRequest):
    db = get_db()
    user = require_login()
    post = await PostService.update(db, user.id, req.post_id, req.title, req.content)
    return BaseResponse(data={
        "id": post.id,
        "title": post.title,
        "content": post.content,
    })


@router.post("/delete")
async def delete_post(req: PostDeleteRequest):
    db = get_db()
    user = require_login()
    await PostService.delete(db, user.id, req.post_id)
    return BaseResponse(message="删除成功")
```

- [ ] **Step 3: 提交**

```bash
git add app/services/post_service.py app/api/routes/post_route.py
git commit -m "feat: post module — CRUD with list/detail"
```

---

## Task 13: 评论模块 — Service + Route

**Files:**
- Create: `app/services/comment_service.py`
- Create: `app/api/routes/comment_route.py`

- [ ] **Step 1: 实现 comment_service.py**

```python
# app/services/comment_service.py
from datetime import datetime, timezone
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment_model import CommentModel
from app.models.post_model import PostModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class CommentService:
    @staticmethod
    async def create(db: AsyncSession, user_id: int, post_id: int, content: str) -> CommentModel:
        # 验证帖子存在
        post_result = await db.execute(
            select(PostModel).where(PostModel.id == post_id, PostModel.deleted_at.is_(None))
        )
        if post_result.scalar_one_or_none() is None:
            raise ApiBusinessException(*ErrorCode.POST_NOT_FOUND)

        comment = CommentModel(
            post_id=post_id,
            user_id=user_id,
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        db.add(comment)
        await db.flush()

        # 更新帖子评论计数
        await db.execute(
            update(PostModel).where(PostModel.id == post_id).values(comment_count=PostModel.comment_count + 1)
        )
        await db.flush()
        return comment

    @staticmethod
    async def get_list(db: AsyncSession, post_id: int, page: int, page_size: int) -> tuple[list[CommentModel], int]:
        total_result = await db.execute(
            select(func.count()).select_from(CommentModel).where(
                CommentModel.post_id == post_id, CommentModel.deleted_at.is_(None)
            )
        )
        total = total_result.scalar()

        result = await db.execute(
            select(CommentModel)
            .where(CommentModel.post_id == post_id, CommentModel.deleted_at.is_(None))
            .order_by(CommentModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def delete(db: AsyncSession, user_id: int, comment_id: int):
        result = await db.execute(
            select(CommentModel).where(CommentModel.id == comment_id, CommentModel.deleted_at.is_(None))
        )
        comment = result.scalar_one_or_none()
        if comment is None:
            raise ApiBusinessException(*ErrorCode.COMMENT_NOT_FOUND)
        if comment.user_id != user_id:
            raise ApiBusinessException(*ErrorCode.NO_PERMISSION)
        comment.deleted_at = datetime.now(timezone.utc)

        # 更新帖子评论计数
        await db.execute(
            update(PostModel).where(PostModel.id == comment.post_id).values(comment_count=PostModel.comment_count - 1)
        )
        await db.flush()
```

- [ ] **Step 2: 创建 comment_route.py**

```python
# app/api/routes/comment_route.py
from fastapi import APIRouter
from app.schemas.comment_schema import CommentCreateRequest, CommentDeleteRequest, CommentListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.comment_service import CommentService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/comment", tags=["评论"])


@router.post("/create")
async def create_comment(req: CommentCreateRequest):
    db = get_db()
    user = require_login()
    comment = await CommentService.create(db, user.id, req.post_id, req.content)
    return BaseResponse(data={
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
    })


@router.post("/list")
async def comment_list(req: CommentListRequest):
    db = get_db()
    comments, total = await CommentService.get_list(db, req.post_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": c.id,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "content_type": c.content_type,
            "content": c.content,
            "reply_count": c.reply_count,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/delete")
async def delete_comment(req: CommentDeleteRequest):
    db = get_db()
    user = require_login()
    await CommentService.delete(db, user.id, req.comment_id)
    return BaseResponse(message="删除成功")
```

- [ ] **Step 3: 提交**

```bash
git add app/services/comment_service.py app/api/routes/comment_route.py
git commit -m "feat: comment module — create, list, delete"
```

---

## Task 14: 回复模块 — Service + Route

**Files:**
- Create: `app/services/reply_service.py`
- Create: `app/api/routes/reply_route.py`

- [ ] **Step 1: 实现 reply_service.py**

```python
# app/services/reply_service.py
from datetime import datetime, timezone
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reply_model import ReplyModel
from app.models.comment_model import CommentModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class ReplyService:
    @staticmethod
    async def create(db: AsyncSession, user_id: int, comment_id: int, content: str, reply_to_user_id: int | None = None) -> ReplyModel:
        # 验证评论存在
        comment_result = await db.execute(
            select(CommentModel).where(CommentModel.id == comment_id, CommentModel.deleted_at.is_(None))
        )
        if comment_result.scalar_one_or_none() is None:
            raise ApiBusinessException(*ErrorCode.COMMENT_NOT_FOUND)

        reply = ReplyModel(
            comment_id=comment_id,
            user_id=user_id,
            reply_to_user_id=reply_to_user_id,
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        db.add(reply)
        await db.flush()

        # 更新评论回复计数
        await db.execute(
            update(CommentModel).where(CommentModel.id == comment_id).values(reply_count=CommentModel.reply_count + 1)
        )
        await db.flush()
        return reply

    @staticmethod
    async def get_list(db: AsyncSession, comment_id: int, page: int, page_size: int) -> tuple[list[ReplyModel], int]:
        total_result = await db.execute(
            select(func.count()).select_from(ReplyModel).where(
                ReplyModel.comment_id == comment_id, ReplyModel.deleted_at.is_(None)
            )
        )
        total = total_result.scalar()

        result = await db.execute(
            select(ReplyModel)
            .where(ReplyModel.comment_id == comment_id, ReplyModel.deleted_at.is_(None))
            .order_by(ReplyModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def delete(db: AsyncSession, user_id: int, reply_id: int):
        result = await db.execute(
            select(ReplyModel).where(ReplyModel.id == reply_id, ReplyModel.deleted_at.is_(None))
        )
        reply = result.scalar_one_or_none()
        if reply is None:
            raise ApiBusinessException(*ErrorCode.REPLY_NOT_FOUND)
        if reply.user_id != user_id:
            raise ApiBusinessException(*ErrorCode.NO_PERMISSION)
        reply.deleted_at = datetime.now(timezone.utc)

        # 更新评论回复计数
        await db.execute(
            update(CommentModel).where(CommentModel.id == reply.comment_id).values(reply_count=CommentModel.reply_count - 1)
        )
        await db.flush()
```

- [ ] **Step 2: 创建 reply_route.py**

```python
# app/api/routes/reply_route.py
from fastapi import APIRouter
from app.schemas.reply_schema import ReplyCreateRequest, ReplyDeleteRequest, ReplyListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.reply_service import ReplyService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/reply", tags=["回复"])


@router.post("/create")
async def create_reply(req: ReplyCreateRequest):
    db = get_db()
    user = require_login()
    reply = await ReplyService.create(db, user.id, req.comment_id, req.content, req.reply_to_user_id)
    return BaseResponse(data={
        "id": reply.id,
        "comment_id": reply.comment_id,
        "content": reply.content,
    })


@router.post("/list")
async def reply_list(req: ReplyListRequest):
    db = get_db()
    replies, total = await ReplyService.get_list(db, req.comment_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": r.id,
            "comment_id": r.comment_id,
            "user_id": r.user_id,
            "reply_to_user_id": r.reply_to_user_id,
            "content_type": r.content_type,
            "content": r.content,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in replies
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/delete")
async def delete_reply(req: ReplyDeleteRequest):
    db = get_db()
    user = require_login()
    await ReplyService.delete(db, user.id, req.reply_id)
    return BaseResponse(message="删除成功")
```

- [ ] **Step 3: 提交**

```bash
git add app/services/reply_service.py app/api/routes/reply_route.py
git commit -m "feat: reply module — create, list, delete"
```

---

## Task 15: 点赞模块 — Service + Route

**Files:**
- Create: `app/services/like_service.py`
- Create: `app/api/routes/like_route.py`

- [ ] **Step 1: 实现 like_service.py**

```python
# app/services/like_service.py
from datetime import datetime, timezone
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like_model import LikeModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.reply_model import ReplyModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode

# target_type 对应的计数字段和模型
TARGET_CONFIG = {
    1: (PostModel, PostModel.like_count, PostModel.id),
    2: (CommentModel, None, CommentModel.id),
    3: (ReplyModel, None, ReplyModel.id),
}


class LikeService:
    @staticmethod
    async def do_like(db: AsyncSession, user_id: int, target_type: int, target_id: int):
        # 检查是否已点赞
        result = await db.execute(
            select(LikeModel).where(
                LikeModel.user_id == user_id,
                LikeModel.target_type == target_type,
                LikeModel.target_id == target_id,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise ApiBusinessException(*ErrorCode.ALREADY_LIKED)

        like = LikeModel(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(like)

        # 帖子点赞更新计数
        if target_type == 1:
            await db.execute(
                update(PostModel).where(PostModel.id == target_id).values(like_count=PostModel.like_count + 1)
            )
        await db.flush()

    @staticmethod
    async def cancel_like(db: AsyncSession, user_id: int, target_type: int, target_id: int):
        result = await db.execute(
            select(LikeModel).where(
                LikeModel.user_id == user_id,
                LikeModel.target_type == target_type,
                LikeModel.target_id == target_id,
            )
        )
        like = result.scalar_one_or_none()
        if like is None:
            raise ApiBusinessException(*ErrorCode.NOT_LIKED)

        await db.delete(like)

        # 帖子点赞更新计数
        if target_type == 1:
            await db.execute(
                update(PostModel).where(PostModel.id == target_id).values(like_count=PostModel.like_count - 1)
            )
        await db.flush()
```

- [ ] **Step 2: 创建 like_route.py**

```python
# app/api/routes/like_route.py
from fastapi import APIRouter
from app.schemas.like_schema import LikeDoRequest, LikeCancelRequest
from app.schemas.common_schema import BaseResponse
from app.services.like_service import LikeService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/like", tags=["点赞"])


@router.post("/do")
async def do_like(req: LikeDoRequest):
    db = get_db()
    user = require_login()
    await LikeService.do_like(db, user.id, req.target_type, req.target_id)
    return BaseResponse(message="点赞成功")


@router.post("/cancel")
async def cancel_like(req: LikeCancelRequest):
    db = get_db()
    user = require_login()
    await LikeService.cancel_like(db, user.id, req.target_type, req.target_id)
    return BaseResponse(message="取消点赞成功")
```

- [ ] **Step 3: 提交**

```bash
git add app/services/like_service.py app/api/routes/like_route.py
git commit -m "feat: like module — do/cancel with atomic counter"
```

---

## Task 16: 收藏模块 — Service + Route

**Files:**
- Create: `app/services/favorite_service.py`
- Create: `app/api/routes/favorite_route.py`

- [ ] **Step 1: 实现 favorite_service.py**

```python
# app/services/favorite_service.py
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite_model import FavoriteModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class FavoriteService:
    @staticmethod
    async def do_favorite(db: AsyncSession, user_id: int, post_id: int):
        result = await db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.post_id == post_id,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise ApiBusinessException(*ErrorCode.ALREADY_FAVORITED)

        fav = FavoriteModel(
            user_id=user_id,
            post_id=post_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(fav)
        await db.flush()

    @staticmethod
    async def cancel_favorite(db: AsyncSession, user_id: int, post_id: int):
        result = await db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.post_id == post_id,
            )
        )
        fav = result.scalar_one_or_none()
        if fav is None:
            raise ApiBusinessException(*ErrorCode.NOT_FAVORITED)
        await db.delete(fav)
        await db.flush()

    @staticmethod
    async def get_list(db: AsyncSession, user_id: int, page: int, page_size: int) -> tuple[list[FavoriteModel], int]:
        total_result = await db.execute(
            select(func.count()).select_from(FavoriteModel).where(FavoriteModel.user_id == user_id)
        )
        total = total_result.scalar()

        result = await db.execute(
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total
```

- [ ] **Step 2: 创建 favorite_route.py**

```python
# app/api/routes/favorite_route.py
from fastapi import APIRouter
from app.schemas.favorite_schema import FavoriteDoRequest, FavoriteCancelRequest, FavoriteListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.favorite_service import FavoriteService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/favorite", tags=["收藏"])


@router.post("/do")
async def do_favorite(req: FavoriteDoRequest):
    db = get_db()
    user = require_login()
    await FavoriteService.do_favorite(db, user.id, req.post_id)
    return BaseResponse(message="收藏成功")


@router.post("/cancel")
async def cancel_favorite(req: FavoriteCancelRequest):
    db = get_db()
    user = require_login()
    await FavoriteService.cancel_favorite(db, user.id, req.post_id)
    return BaseResponse(message="取消收藏成功")


@router.post("/list")
async def favorite_list(req: FavoriteListRequest):
    db = get_db()
    favs, total = await FavoriteService.get_list(db, req.user_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": f.id,
            "user_id": f.user_id,
            "post_id": f.post_id,
            "created_at": f.created_at.isoformat(),
        }
        for f in favs
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())
```

- [ ] **Step 3: 提交**

```bash
git add app/services/favorite_service.py app/api/routes/favorite_route.py
git commit -m "feat: favorite module — do/cancel/list"
```

---

## Task 17: Main App 组装

**Files:**
- Create: `app/main.py`
- Modify: `app/api/routes/__init__.py`

- [ ] **Step 1: 更新 routes/__init__.py 注册路由**

```python
# app/api/routes/__init__.py
from fastapi import APIRouter
from app.api.routes.auth_route import router as auth_router
from app.api.routes.post_route import router as post_router
from app.api.routes.comment_route import router as comment_router
from app.api.routes.reply_route import router as reply_router
from app.api.routes.like_route import router as like_router
from app.api.routes.favorite_route import router as favorite_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(post_router)
api_router.include_router(comment_router)
api_router.include_router(reply_router)
api_router.include_router(like_router)
api_router.include_router(favorite_router)
```

- [ ] **Step 2: 创建 main.py**

```python
# app/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.exceptions import ApiBusinessException
from app.middleware.db_session import DBSessionMiddleware
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("community")

app = FastAPI(title="Community API", version="0.1.0")

# 中间件（执行顺序：后添加先执行）
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(DBSessionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(api_router)


# 异常处理器
@app.exception_handler(ApiBusinessException)
async def business_exception_handler(request: Request, exc: ApiBusinessException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(Exception)
async def system_exception_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "message": "系统异常", "data": None},
    )
```

- [ ] **Step 3: 验证应用启动**

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl -s http://localhost:8000/docs | head -5
kill %1
```

Expected: 返回 FastAPI Swagger 文档页 HTML

- [ ] **Step 4: 提交**

```bash
git add app/main.py app/api/routes/__init__.py
git commit -m "feat: FastAPI app assembly with all routes and middleware"
```

---

## Task 18: Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`

- [ ] **Step 1: 创建 Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app/ ./app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: community
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/community
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: change-me-in-production
      DEBUG: "false"

volumes:
  pgdata:
```

- [ ] **Step 3: 启动验证**

```bash
docker compose up -d
sleep 5
curl -s http://localhost:8000/docs | head -5
docker compose down
```

Expected: 返回 FastAPI 文档页 HTML

- [ ] **Step 4: 提交**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: Docker Compose with PostgreSQL, Redis, and app"
```

---

## Task 19: 集成测试 — Auth API

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_api/__init__.py`
- Create: `tests/test_api/test_auth_api.py`

- [ ] **Step 1: 创建测试 fixtures**

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.base import Base
from app.core.context import db_session_var, current_user_var

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/community_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        db_session_var.set(session)
        yield session
        current_user_var.set(None)


@pytest.fixture
async def client(test_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 2: 写集成测试**

```python
# tests/test_api/test_auth_api.py
import pytest


@pytest.mark.asyncio
async def test_login_register_new_user(client):
    """新邮箱注册并登录"""
    response = await client.post("/api/auth/login", json={
        "email": "test_new@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "test_new@example.com"


@pytest.mark.asyncio
async def test_login_existing_user(client):
    """已注册用户登录"""
    # 先注册
    await client.post("/api/auth/login", json={
        "email": "test_exist@example.com",
        "password": "password123"
    })
    # 再登录
    response = await client.post("/api/auth/login", json={
        "email": "test_exist@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """密码错误"""
    await client.post("/api/auth/login", json={
        "email": "test_wrong@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login", json={
        "email": "test_wrong@example.com",
        "password": "wrong-password"
    })
    assert response.status_code == 200
    assert response.json()["code"] == 2002


@pytest.mark.asyncio
async def test_me_without_auth(client):
    """未登录获取个人信息"""
    response = await client.post("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["code"] == 2001


@pytest.mark.asyncio
async def test_me_with_auth(client):
    """已登录获取个人信息"""
    login_resp = await client.post("/api/auth/login", json={
        "email": "test_me@example.com",
        "password": "password123"
    })
    token = login_resp.json()["data"]["token"]

    response = await client.post(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert response.json()["data"]["email"] == "test_me@example.com"
```

- [ ] **Step 3: 运行集成测试**

```bash
uv run pytest tests/test_api/test_auth_api.py -v
```

Expected: 5 passed（需要 PostgreSQL test 数据库运行中）

- [ ] **Step 4: 提交**

```bash
git add tests/conftest.py tests/test_api/
git commit -m "test: auth API integration tests"
```

---

## Task 20: 最终验证

- [ ] **Step 1: 运行所有测试**

```bash
uv run pytest -v
```

Expected: All tests passed

- [ ] **Step 2: 本地启动验证**

```bash
docker compose up -d
sleep 5
# 注册+登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'
```

Expected: 返回 token 和用户信息

- [ ] **Step 3: 清理并提交**

```bash
docker compose down
git add -A
git commit -m "chore: final validation cleanup"
```
