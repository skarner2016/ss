from fastapi import APIRouter
from app.schemas.like_schema import LikeDoRequest, LikeCancelRequest
from app.schemas.common_schema import BaseResponse
from app.services.like_service import LikeService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/like", tags=["点赞"])


@router.post("/do")
async def do_like(req: LikeDoRequest):
    db = get_db()
    user = require_login()
    await LikeService.do_like(db, user.id, req.target_type, req.target_id)
    return BaseResponse(message="点赞成功")


@router.post("/cancel")
async def cancel_like(req: LikeCancelRequest):
    db = get_db()
    user = require_login()
    await LikeService.cancel_like(db, user.id, req.target_type, req.target_id)
    return BaseResponse(message="取消点赞成功")
