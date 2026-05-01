from datetime import datetime, timezone
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like_model import LikeModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.reply_model import ReplyModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode

TARGET_CONFIG = {
    1: (PostModel, PostModel.like_count, PostModel.id),
    2: (CommentModel, None, CommentModel.id),
    3: (ReplyModel, None, ReplyModel.id),
}


class LikeService:
    @staticmethod
    async def do_like(db: AsyncSession, user_id: int, target_type: int, target_id: int):
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

        if target_type == 1:
            await db.execute(
                update(PostModel).where(PostModel.id == target_id).values(like_count=PostModel.like_count - 1)
            )
        await db.flush()
