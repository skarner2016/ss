from fastapi import APIRouter
from app.schemas.favorite_schema import FavoriteDoRequest, FavoriteCancelRequest, FavoriteListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.favorite_service import FavoriteService
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
    favs, total = await FavoriteService.get_list(db, req.user_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": f.id,
            "user_id": f.user_id,
            "post_id": f.post_id,
            "created_at": f.created_at.isoformat(),
        }
        for f in favs
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())
