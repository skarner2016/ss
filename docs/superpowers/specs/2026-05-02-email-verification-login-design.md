# Email Verification Code Login Design

**Date:** 2026-05-02

**Goal:** Replace password-based login with email verification code login. User receives a 6-digit code via Resend email, enters it to log in (or auto-register on first use).

**Approach:** Two-step login flow — email → send code → enter code → login/register.

---

## Changes Summary

| Area | Change |
|------|--------|
| User model | Remove `password_hash` field entirely |
| Database | Alembic migration: drop `password_hash` column |
| Backend auth | New `send_code` endpoint, modify `login` to accept `code` instead of `password` |
| Security utils | Remove `hash_password` / `verify_password` functions |
| Redis | Store verification codes with 10-minute TTL, delete on successful use |
| Email | Send 6-digit code via Resend |
| Frontend login | Two-step UI (email → code), no password field |
| Frontend store | Update `login(email, code)` signature |

---

## Backend

### Database: User Model (`backend/app/models/user_model.py`)

Remove `password_hash` field from `UserModel`:

```python
class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    status = Column(SmallInteger, default=1, comment="0=disabled 1=active 2=cancelled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Alembic Migration

```sql
ALTER TABLE users DROP COLUMN password_hash;
```

Generate via: `alembic revision --autogenerate -m "drop password_hash column"`

### Verification Code Service (`backend/app/services/code_service.py`)

Redis key pattern: `auth:code:{email}` — value is the 6-digit code string.

```python
import random, string, redis.asyncio as aioredis

CODE_TTL = 600  # 10 minutes
CODE_LENGTH = 6

async def send_code(email: str) -> None:
    code = ''.join(random.choices(string.digits, k=CODE_LENGTH))
    r = aioredis.from_url(settings.redis_url)
    await r.set(f"auth:code:{email}", code, ex=CODE_TTL)
    # Send email via Resend
    resend.emails.send(from_=settings.resend_from_email, to=email, subject="Your login code", html=code_html(code))
    await r.aclose()

async def verify_code(email: str, code: str) -> bool:
    r = aioredis.from_url(settings.redis_url)
    stored = await r.get(f"auth:code:{email}")
    if stored and stored.decode() == code:
        await r.delete(f"auth:code:{email}")  # One-time use
        await r.aclose()
        return True
    await r.aclose()
    return False
```

### Auth Routes (`backend/app/api/routes/auth_route.py`)

**New endpoint:**
```
POST /api/auth/send_code
Body: { "email": "user@example.com" }
Response: { "message": "ok" }
```

**Modified endpoint:**
```
POST /api/auth/login
Body: { "email": "user@example.com", "code": "123456" }
Response: { "token": "...", "user": { ... } }
```

Logic:
1. Call `verify_code(email, code)` — returns `True`/`False`
2. If `False`: return 401 "验证码错误或已过期"
3. If `True`: find user by email; if not found, create user (no password_hash)
4. Sign JWT and return token + user

### Settings (`backend/app/core/config.py`)

Add fields:
```python
RESEND_API_KEY: str = ""
RESEND_FROM_EMAIL: str = "noreply@yourdomain.com"
CODE_TTL: int = 600  # seconds
CODE_LENGTH: int = 6
```

### Resend Integration

```
pip install resend
```

```python
import resend
resend.api_key = settings.RESEND_API_KEY

def send_verification_email(to: str, code: str):
    resend.emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to],
        "subject": "Your login code",
        "html": f"<p>Your verification code is <strong>{code}</strong>. It expires in 10 minutes.</p>"
    })
```

---

## Frontend

### Login Page (`front/src/pages/Login.vue`)

Two-step UI:
- **Step 1:** Email input + "发送验证码" button. After send, transition to Step 2.
- **Step 2:** 6-digit code input (single or split boxes) + "登录" button. Show countdown timer (60s) on "重新发送" link.

### API (`front/src/api/auth.ts`)

```typescript
export function sendCode(email: string) {
  return request.post('/auth/send_code', { email })
}

export function login(email: string, code: string) {
  return request.post('/auth/login', { email, code })
}
```

### Auth Store (`front/src/stores/auth.ts`)

```typescript
login(email: string, code: string) // changed from password to code
```

Remove all password-related references from the store.

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Invalid email format | 400 "邮箱格式不正确" |
| Code expired or not found | 401 "验证码错误或已过期" |
| Code mismatch | 401 "验证码错误或已过期" |
| Resend API failure | 500 "邮件发送失败，请稍后重试" |
| Too many sends | Rate limit: max 5 per email per 10 minutes (stored in Redis) |

---

## Security

- Code is one-time use (deleted from Redis after successful verification)
- Code expires after 10 minutes
- Rate limit: max 5 send requests per email per 10 minutes
- Code is 6 digits (1M combinations, brute-force protection via rate limiting)
