import secrets
import string
import resend
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

    # Generate code
    code = "".join(secrets.choice(string.digits) for _ in range(settings.code_length))

    # Send email via Resend first, store code only on success
    try:
        resend.api_key = settings.resend_api_key
        resend.emails.send({
            "from": settings.resend_from_email,
            "to": [email],
            "subject": "Your login code",
            "html": f"<p>Your verification code is <strong>{code}</strong>. It expires in {settings.code_ttl // 60} minutes.</p>",
        })
    except Exception as e:
        raise ApiBusinessException(*ErrorCode.CODE_SEND_FAILED)

    await r.set(f"auth:code:{email}", code, ex=settings.code_ttl)


async def verify_code(email: str, code: str) -> bool:
    r = await get_redis()
    stored = await r.get(f"auth:code:{email}")
    if stored and stored == code:
        await r.delete(f"auth:code:{email}")
        return True
    return False
