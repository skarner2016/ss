from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel_model import ChannelModel, PostChannelModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class ChannelService:
    @staticmethod
    async def create(db: AsyncSession, name: str, description: str | None, sort_order: int) -> ChannelModel:
        existing = await db.execute(select(ChannelModel).where(ChannelModel.name == name))
        if existing.scalar_one_or_none() is not None:
            raise ApiBusinessException(*ErrorCode.CHANNEL_NAME_EXISTS)
        channel = ChannelModel(
            name=name,
            description=description,
            sort_order=sort_order,
            status=1,
            created_at=datetime.now(timezone.utc),
        )
        db.add(channel)
        await db.flush()
        return channel

    @staticmethod
    async def get_or_raise(db: AsyncSession, channel_id: int) -> ChannelModel:
        result = await db.execute(select(ChannelModel).where(ChannelModel.id == channel_id))
        channel = result.scalar_one_or_none()
        if channel is None:
            raise ApiBusinessException(*ErrorCode.CHANNEL_NOT_FOUND)
        return channel

    @staticmethod
    async def update(db: AsyncSession, channel_id: int, name: str | None, description: str | None,
                     sort_order: int | None, status: int | None) -> ChannelModel:
        channel = await ChannelService.get_or_raise(db, channel_id)
        if name is not None and name != channel.name:
            existing = await db.execute(select(ChannelModel).where(ChannelModel.name == name))
            if existing.scalar_one_or_none() is not None:
                raise ApiBusinessException(*ErrorCode.CHANNEL_NAME_EXISTS)
            channel.name = name
        if description is not None:
            channel.description = description
        if sort_order is not None:
            channel.sort_order = sort_order
        if status is not None:
            channel.status = status
        await db.flush()
        return channel

    @staticmethod
    async def delete(db: AsyncSession, channel_id: int):
        channel = await ChannelService.get_or_raise(db, channel_id)
        count_result = await db.execute(
            select(func.count()).select_from(PostChannelModel).where(PostChannelModel.channel_id == channel_id)
        )
        if count_result.scalar() > 0:
            raise ApiBusinessException(*ErrorCode.CHANNEL_HAS_POSTS)
        await db.delete(channel)
        await db.flush()

    @staticmethod
    async def get_list(db: AsyncSession, page: int, page_size: int) -> tuple[list[ChannelModel], int]:
        total_result = await db.execute(select(func.count()).select_from(ChannelModel))
        total = total_result.scalar()
        result = await db.execute(
            select(ChannelModel)
            .order_by(ChannelModel.sort_order.asc(), ChannelModel.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def get_public_list(db: AsyncSession) -> list[ChannelModel]:
        result = await db.execute(
            select(ChannelModel)
            .where(ChannelModel.status == 1)
            .order_by(ChannelModel.sort_order.asc(), ChannelModel.id.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def validate_channel_ids(db: AsyncSession, channel_ids: list[int]) -> None:
        if len(channel_ids) > 3:
            raise ApiBusinessException(*ErrorCode.POST_CHANNEL_LIMIT)
        if not channel_ids:
            return
        result = await db.execute(
            select(ChannelModel).where(ChannelModel.id.in_(channel_ids))
        )
        found = result.scalars().all()
        if len(found) != len(channel_ids):
            raise ApiBusinessException(*ErrorCode.POST_CHANNEL_INVALID)

    @staticmethod
    async def set_post_channels(db: AsyncSession, post_id: int, channel_ids: list[int]) -> None:
        await db.execute(
            PostChannelModel.__table__.delete().where(PostChannelModel.post_id == post_id)
        )
        for cid in channel_ids:
            db.add(PostChannelModel(post_id=post_id, channel_id=cid))
        await db.flush()

    @staticmethod
    async def get_channels_for_posts(db: AsyncSession, post_ids: list[int]) -> dict[int, list[dict]]:
        if not post_ids:
            return {}
        result = await db.execute(
            select(PostChannelModel.post_id, ChannelModel.id, ChannelModel.name)
            .join(ChannelModel, ChannelModel.id == PostChannelModel.channel_id)
            .where(PostChannelModel.post_id.in_(post_ids))
        )
        mapping: dict[int, list[dict]] = {pid: [] for pid in post_ids}
        for row in result.all():
            mapping[row.post_id].append({"id": row.id, "name": row.name})
        return mapping
