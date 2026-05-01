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

        await db.execute(
            update(PostModel).where(PostModel.id == comment.post_id).values(comment_count=PostModel.comment_count - 1)
        )
        await db.flush()
