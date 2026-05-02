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
