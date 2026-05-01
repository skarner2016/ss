from fastapi import APIRouter
from sqlalchemy import select
from app.schemas.favorite_schema import FavoriteDoRequest, FavoriteCancelRequest, FavoriteListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.favorite_service import FavoriteService
from app.models.post_model import PostModel
from app.models.user_model import UserModel
from app.models.like_model import LikeModel
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/favorite", tags=["收藏"])


@router.post("/do")
async def do_favorite(req: FavoriteDoRequest):
    db = get_db()
    user = require_login()
    await FavoriteService.do_favorite(db, user.id, req.post_id)
    return BaseResponse(message="收藏成功")


@router.post("/cancel")
async def cancel_favorite(req: FavoriteCancelRequest):
    db = get_db()
    user = require_login()
    await FavoriteService.cancel_favorite(db, user.id, req.post_id)
    return BaseResponse(message="取消收藏成功")


@router.post("/list")
async def favorite_list(req: FavoriteListRequest):
    db = get_db()
    user = require_login()
    favs, total = await FavoriteService.get_list(db, user.id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size

    post_ids = [f.post_id for f in favs]
    posts: dict[int, PostModel] = {}
    user_map: dict[int, str | None] = {}
    liked_ids: set[int] = set()

    if post_ids:
        post_result = await db.execute(select(PostModel).where(PostModel.id.in_(post_ids)))
        for p in post_result.scalars().all():
            posts[p.id] = p

        user_ids = list({p.user_id for p in posts.values()})
        if user_ids:
            user_result = await db.execute(
                select(UserModel.id, UserModel.nickname).where(UserModel.id.in_(user_ids))
            )
            for row in user_result.all():
                user_map[row.id] = row.nickname

        like_result = await db.execute(
            select(LikeModel.target_id).where(
                LikeModel.user_id == user.id,
                LikeModel.target_type == 1,
                LikeModel.target_id.in_(post_ids),
            )
        )
        liked_ids = {row[0] for row in like_result.all()}

    items = []
    for f in favs:
        p = posts.get(f.post_id)
        if p is None:
            continue
        items.append({
            "id": p.id,
            "user_id": p.user_id,
            "author_nickname": user_map.get(p.user_id),
            "title": p.title,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "is_liked": p.id in liked_ids,
            "is_favorited": True,
            "created_at": p.created_at.isoformat(),
        })

    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())
