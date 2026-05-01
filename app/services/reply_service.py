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

        await db.execute(
            update(CommentModel).where(CommentModel.id == reply.comment_id).values(reply_count=CommentModel.reply_count - 1)
        )
        await db.flush()
