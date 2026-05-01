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
