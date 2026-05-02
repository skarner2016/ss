# Email Verification Code Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace password-based login with email verification code login using Resend.

**Architecture:** Two-step login: email → send code via Resend → enter 6-digit code → verify against Redis → JWT issued. First login auto-registers. Password field removed from user model.

**Tech Stack:** Python/FastAPI, Redis (verification codes), Resend (email), Vue 3 + Element Plus (frontend)

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/core/config.py` | Modify | Add RESEND_API_KEY, RESEND_FROM_EMAIL, CODE_TTL |
| `backend/app/core/security.py` | Modify | Remove hash_password/verify_password |
| `backend/app/core/error_codes.py` | Modify | Add CODE错误/邮件发送失败错误码 |
| `backend/app/schemas/auth_schema.py` | Modify | Change LoginRequest (password→code), add SendCodeRequest |
| `backend/app/models/user_model.py` | Modify | Remove password_hash field |
| `backend/app/services/auth_service.py` | Modify | Replace password auth with code auth |
| `backend/app/services/code_service.py` | Create | Redis code storage + Resend email sending |
| `backend/app/api/routes/auth_route.py` | Modify | Add /send_code endpoint, change /login to use code |
| `backend/pyproject.toml` | Modify | Add resend dependency, remove bcrypt |
| `front/src/api/types.ts` | Modify | Change LoginParams (password→code), add sendCode type |
| `front/src/api/auth.ts` | Modify | Add sendCode function, change login params |
| `front/src/stores/auth.ts` | Modify | Change login signature (password→code) |
| `front/src/pages/Login.vue` | Modify | Two-step UI (email→code) |

---

## Task 1: Add Settings and Dependencies

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: Add Resend settings**

In `backend/app/core/config.py`, add three fields to the Settings class:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "community"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/community"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    resend_api_key: str = ""
    resend_from_email: str = "noreply@yourdomain.com"
    code_ttl: int = 600  # 10 minutes
    code_length: int = 6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 2: Add resend to pyproject.toml, remove bcrypt**

In `backend/pyproject.toml`, replace `"bcrypt>=5.0.0",` with `"resend>=6.0.0",` in dependencies:

```toml
[project]
name = "community"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "asyncpg>=0.31.0",
    "email-validator>=2.3.0",
    "fastapi>=0.136.1",
    "greenlet>=3.5.0",
    "httpx>=0.28.1",
    "pydantic-settings>=2.14.0",
    "pyjwt>=2.12.1",
    "redis>=7.4.0",
    "resend>=6.0.0",
    "sqlalchemy[asyncio]>=2.0.49",
    "uvicorn[standard]>=0.46.0",
]

[dependency-groups]
dev = [
    "httpx>=0.28.1",
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
]
```

- [ ] **Step 3: Install dependencies**

Run: `cd /Users/skarner/workspace/skarner2016/ss/backend && uv sync`

- [ ] **Step 4: Add env vars to docker-compose.yml and .env**

In `backend/app/core/config.py`, the settings already load from `.env` via pydantic-settings. Add to the backend environment in `docker-compose.yml` under `backend.environment`:

```yaml
  backend:
    build: ./backend
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
      RESEND_API_KEY: ${RESEND_API_KEY:-}
      RESEND_FROM_EMAIL: ${RESEND_FROM_EMAIL:-noreply@yourdomain.com}
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/config.py backend/pyproject.toml docker-compose.yml
git commit -m "feat: add Resend settings and remove bcrypt dependency"
```

---

## Task 2: Remove Password from User Model

**Files:**
- Modify: `backend/app/models/user_model.py`
- Modify: `backend/app/core/security.py`
- Modify: `backend/app/core/error_codes.py`
- Modify: `backend/app/schemas/auth_schema.py`

- [ ] **Step 1: Remove password_hash from user model**

In `backend/app/models/user_model.py`:

```python
from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 2: Remove hash_password/verify_password from security.py**

In `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings


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

- [ ] **Step 3: Update error codes**

In `backend/app/core/error_codes.py`, replace `PASSWORD_ERROR` and `PASSWORD_TOO_SHORT` with code-related errors:

```python
class ErrorCode:
    # 参数错误 1xxx
    PARAM_ERROR = (1001, "参数错误")
    EMAIL_FORMAT_ERROR = (1002, "邮箱格式不正确")
    CODE_INVALID = (1003, "验证码错误或已过期")
    CODE_SEND_FAILED = (1004, "邮件发送失败，请稍后重试")
    CODE_RATE_LIMITED = (1005, "发送过于频繁，请稍后重试")

    # 认证错误 2xxx
    UNAUTHORIZED = (2001, "未登录")
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

    # 频道错误 6xxx
    CHANNEL_NOT_FOUND = (6001, "频道不存在")
    CHANNEL_NAME_EXISTS = (6002, "频道名称已存在")
    CHANNEL_HAS_POSTS = (6003, "频道下存在帖子，无法删除")
    POST_CHANNEL_LIMIT = (6004, "每篇帖子最多关联3个频道")
    POST_CHANNEL_INVALID = (6005, "包含无效的频道ID")

    # 系统错误 5xxx
    SYSTEM_ERROR = (5000, "系统异常")
```

- [ ] **Step 4: Update auth schema**

In `backend/app/schemas/auth_schema.py`:

```python
from pydantic import BaseModel, EmailStr, Field


class SendCodeRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


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

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/user_model.py backend/app/core/security.py backend/app/core/error_codes.py backend/app/schemas/auth_schema.py
git commit -m "feat: remove password from user model and update schemas"
```

---

## Task 3: Create Code Service (Redis + Resend)

**Files:**
- Create: `backend/app/services/code_service.py`

- [ ] **Step 1: Create code_service.py**

```python
import random
import string
from app.core.config import settings
from app.core.redis import get_redis
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode

RATE_LIMIT_KEY_PREFIX = "auth:code:rate:"
RATE_LIMIT_MAX = 5
RATE_LIMIT_TTL = 600  # 10 minutes


async def send_code(email: str) -> None:
    r = await get_redis()

    # Rate limit check
    rate_key = f"{RATE_LIMIT_KEY_PREFIX}{email}"
    count = await r.incr(rate_key)
    if count == 1:
        await r.expire(rate_key, RATE_LIMIT_TTL)
    if count > RATE_LIMIT_MAX:
        raise ApiBusinessException(*ErrorCode.CODE_RATE_LIMITED)

    # Generate and store code
    code = "".join(random.choices(string.digits, k=settings.code_length))
    await r.set(f"auth:code:{email}", code, ex=settings.code_ttl)

    # Send email via Resend
    try:
        import resend
        resend.api_key = settings.resend_api_key
        resend.emails.send({
            "from": settings.resend_from_email,
            "to": [email],
            "subject": "Your login code",
            "html": f"<p>Your verification code is <strong>{code}</strong>. It expires in {settings.code_ttl // 60} minutes.</p>",
        })
    except Exception as e:
        raise ApiBusinessException(*ErrorCode.CODE_SEND_FAILED)


async def verify_code(email: str, code: str) -> bool:
    r = await get_redis()
    stored = await r.get(f"auth:code:{email}")
    if stored and stored == code:
        await r.delete(f"auth:code:{email}")
        return True
    return False
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/code_service.py
git commit -m "feat: add verification code service with Redis and Resend"
```

---

## Task 4: Update Auth Service and Routes

**Files:**
- Modify: `backend/app/services/auth_service.py`
- Modify: `backend/app/api/routes/auth_route.py`

- [ ] **Step 1: Update auth_service.py**

```python
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.core.security import create_token
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode
from app.services.code_service import verify_code


class AuthService:
    @staticmethod
    async def login_or_register(db: AsyncSession, email: str, code: str) -> tuple[str, UserModel]:
        verified = await verify_code(email, code)
        if not verified:
            raise ApiBusinessException(*ErrorCode.CODE_INVALID)

        result = await db.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            user = UserModel(
                email=email,
                status=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(user)
            await db.flush()
            user.nickname = f"user_{user.id}"
            await db.flush()
        else:
            if user.status == 0:
                raise ApiBusinessException(*ErrorCode.USER_DISABLED)
            if user.status == 2:
                raise ApiBusinessException(*ErrorCode.USER_CANCELLED)

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

- [ ] **Step 2: Update auth_route.py**

```python
from fastapi import APIRouter
from app.schemas.auth_schema import SendCodeRequest, LoginRequest, UpdateMeRequest
from app.schemas.common_schema import BaseResponse
from app.services.auth_service import AuthService
from app.services.code_service import send_code
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/send_code")
async def send_verification_code(req: SendCodeRequest):
    await send_code(req.email)
    return BaseResponse(data={"message": "ok"})


@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    token, user = await AuthService.login_or_register(db, req.email, req.code)
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


@router.post("/user_info")
async def user_info(user_id: int):
    db = get_db()
    user = await AuthService.get_user_info(db, user_id)
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

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/auth_service.py backend/app/api/routes/auth_route.py
git commit -m "feat: update auth service and routes for verification code login"
```

---

## Task 5: Update Frontend API and Store

**Files:**
- Modify: `front/src/api/types.ts`
- Modify: `front/src/api/auth.ts`
- Modify: `front/src/stores/auth.ts`

- [ ] **Step 1: Update LoginParams in types.ts**

In `front/src/api/types.ts`, change `LoginParams`:

```typescript
export interface SendCodeParams {
  email: string
}

export interface LoginParams {
  email: string
  code: string
}
```

- [ ] **Step 2: Add sendCode to auth.ts API**

In `front/src/api/auth.ts`:

```typescript
import request from './request'
import type { SendCodeParams, LoginParams, LoginResult, User, UpdateMeParams } from './types'

export function sendCode(data: SendCodeParams) {
  return request.post<any, { message: string }>('/auth/send_code', data)
}

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
```

- [ ] **Step 3: Update auth store**

In `front/src/stores/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/types'
import { login as apiLogin, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(email: string, code: string) {
    const result = await apiLogin({ email, code })
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

- [ ] **Step 4: Commit**

```bash
git add front/src/api/types.ts front/src/api/auth.ts front/src/stores/auth.ts
git commit -m "feat: update frontend API and store for verification code login"
```

---

## Task 6: Update Login Page UI

**Files:**
- Modify: `front/src/pages/Login.vue`

- [ ] **Step 1: Rewrite Login.vue with two-step UI**

```vue
<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="login-title">社区</h2>

      <!-- Step 1: Email -->
      <el-form v-if="step === 1" ref="emailFormRef" :model="emailForm" :rules="emailRules" @submit.prevent="handleSendCode">
        <el-form-item prop="email">
          <el-input v-model="emailForm.email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="sending" native-type="submit" style="width: 100%">
            发送验证码
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Step 2: Code -->
      <el-form v-else ref="codeFormRef" :model="codeForm" :rules="codeRules" @submit.prevent="handleLogin">
        <div class="code-email-hint">
          验证码已发送至 <strong>{{ emailForm.email }}</strong>
        </div>
        <el-form-item prop="code">
          <el-input v-model="codeForm.code" placeholder="6位验证码" size="large" maxlength="6" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="logging" native-type="submit" style="width: 100%">
            登录 / 注册
          </el-button>
        </el-form-item>
        <div class="resend-row">
          <span v-if="countdown > 0" class="countdown">{{ countdown }}s 后可重发</span>
          <el-button v-else text type="primary" @click="handleSendCode">重新发送</el-button>
          <el-button text @click="step = 1">更换邮箱</el-button>
        </div>
      </el-form>

      <p class="login-hint">首次登录将自动注册</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { sendCode } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const step = ref(1)
const sending = ref(false)
const logging = ref(false)
const countdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

const emailFormRef = ref<FormInstance>()
const codeFormRef = ref<FormInstance>()

const emailForm = reactive({ email: '' })
const codeForm = reactive({ code: '' })

const emailRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

const codeRules: FormRules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

function startCountdown() {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

async function handleSendCode() {
  const valid = await emailFormRef.value?.validate().catch(() => false)
  if (!valid) return

  sending.value = true
  try {
    await sendCode({ email: emailForm.email })
    step.value = 2
    startCountdown()
  } finally {
    sending.value = false
  }
}

async function handleLogin() {
  const valid = await codeFormRef.value?.validate().catch(() => false)
  if (!valid) return

  logging.value = true
  try {
    await authStore.login(emailForm.email, codeForm.code)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } finally {
    logging.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 56px);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--color-primary);
}

.code-email-hint {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.resend-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.countdown {
  color: var(--color-text-muted);
  font-size: 13px;
}

.login-hint {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 12px;
  margin-top: 0;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add front/src/pages/Login.vue
git commit -m "feat: update login page to two-step verification code UI"
```

---

## Task 7: Update Tests

**Files:**
- Modify: `backend/tests/test_core/test_error_codes.py`
- Modify: `backend/tests/test_core/test_security.py`
- Modify: `backend/tests/test_services/test_auth_service.py`

- [ ] **Step 1: Read current test files**

```bash
cat backend/tests/test_core/test_error_codes.py
cat backend/tests/test_core/test_security.py
cat backend/tests/test_services/test_auth_service.py
```

- [ ] **Step 2: Remove PASSWORD_ERROR test from test_error_codes.py**

Remove any test that references `ErrorCode.PASSWORD_ERROR` or `ErrorCode.PASSWORD_TOO_SHORT`. Add tests for the new error codes:

```python
def test_code_invalid_error():
    code, message = ErrorCode.CODE_INVALID
    assert code == 1003
    assert message == "验证码错误或已过期"

def test_code_send_failed_error():
    code, message = ErrorCode.CODE_SEND_FAILED
    assert code == 1004
    assert message == "邮件发送失败，请稍后重试"
```

- [ ] **Step 3: Remove password tests from test_security.py**

Remove `test_hash_and_verify_password` and any test that imports `hash_password` or `verify_password`. Keep `test_create_token` and `test_decode_token` tests unchanged.

- [ ] **Step 4: Update test_auth_service.py**

Remove any test that creates a `UserModel` with `password_hash=...`. Update tests to use the new code-based login flow. Since `verify_code` calls Redis, mock it:

```python
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.core.exceptions import ApiBusinessException


@pytest.mark.asyncio
async def test_login_with_invalid_code(mock_db: AsyncSession):
    with patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=False)):
        with pytest.raises(ApiBusinessException) as exc_info:
            await AuthService.login_or_register(mock_db, "test@example.com", "000000")
        assert exc_info.value.code == 1003


@pytest.mark.asyncio
async def test_login_creates_new_user(mock_db: AsyncSession):
    with patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True)):
        # mock db.execute to return no user
        # then verify user is created
        pass  # implement based on existing conftest.py patterns
```

- [ ] **Step 5: Run tests**

```bash
cd /Users/skarner/workspace/skarner2016/ss/backend && uv run pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/tests/
git commit -m "test: update tests for verification code login"
```

---

## Task 8: Docker Build and Verify

- [ ] **Step 1: Drop password_hash column from database**

Since there is no Alembic setup, run a direct SQL migration. Connect to the database and execute:

```bash
docker compose exec db psql -U postgres -d community -c "ALTER TABLE users DROP COLUMN IF EXISTS password_hash;"
```

- [ ] **Step 2: Rebuild and restart all services**

```bash
docker compose build backend front
docker compose up -d
```

- [ ] **Step 3: Verify backend starts without errors**

```bash
docker compose logs backend --tail 20
```

Expected: Server starts, no import errors.

- [ ] **Step 4: Test send_code endpoint**

```bash
curl -X POST http://localhost:8000/api/auth/send_code \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

Expected: `{"code": 0, "message": "OK", "data": {"message": "ok"}}` (requires valid RESEND_API_KEY)

- [ ] **Step 5: Test login endpoint with invalid code**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "code": "000000"}'
```

Expected: `{"code": 2002, "message": "验证码错误或已过期"}`

- [ ] **Step 6: Test frontend login flow**

Open `http://localhost:80`, click login, enter email, send code, enter code. Verify redirect to home.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: verify email verification code login end-to-end"
```

---

## Type Consistency Check

- `auth_service.login_or_register(db, email, code)` — matches `LoginRequest.code: str`
- `auth_route.login(req: LoginRequest)` passes `req.code` — matches service
- `code_service.send_code(email: str)` — matches `SendCodeRequest.email: str`
- `auth_route.send_verification_code(req: SendCodeRequest)` calls `send_code(req.email)` — matches
- `stores/auth.ts login(email, code)` calls `apiLogin({ email, code })` — matches `LoginParams`
- `Login.vue` calls `authStore.login(emailForm.email, codeForm.code)` — matches store
- `Login.vue` calls `sendCode({ email: emailForm.email })` — matches API
- `ErrorCodes.CODE_INVALID (1003)` used in `auth_service.py` — matches
