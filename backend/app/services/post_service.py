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
    async def get_list(db: AsyncSession, page: int, page_size: int, channel_id: int | None = None) -> tuple[list[PostModel], int]:
        from app.models.channel_model import PostChannelModel
        base_filter = PostModel.deleted_at.is_(None)

        if channel_id is not None:
            count_stmt = (
                select(func.count())
                .select_from(PostModel)
                .join(PostChannelModel, PostChannelModel.post_id == PostModel.id)
                .where(base_filter, PostChannelModel.channel_id == channel_id)
            )
            list_stmt = (
                select(PostModel)
                .join(PostChannelModel, PostChannelModel.post_id == PostModel.id)
                .where(base_filter, PostChannelModel.channel_id == channel_id)
                .order_by(PostModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        else:
            count_stmt = select(func.count()).select_from(PostModel).where(base_filter)
            list_stmt = (
                select(PostModel)
                .where(base_filter)
                .order_by(PostModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )

        total = (await db.execute(count_stmt)).scalar()
        posts = (await db.execute(list_stmt)).scalars().all()
        return posts, total

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
