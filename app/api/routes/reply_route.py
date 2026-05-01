from fastapi import APIRouter
from app.schemas.reply_schema import ReplyCreateRequest, ReplyDeleteRequest, ReplyListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.reply_service import ReplyService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/reply", tags=["回复"])


@router.post("/create")
async def create_reply(req: ReplyCreateRequest):
    db = get_db()
    user = require_login()
    reply = await ReplyService.create(db, user.id, req.comment_id, req.content, req.reply_to_user_id)
    return BaseResponse(data={
        "id": reply.id,
        "comment_id": reply.comment_id,
        "content": reply.content,
    })


@router.post("/list")
async def reply_list(req: ReplyListRequest):
    db = get_db()
    replies, total = await ReplyService.get_list(db, req.comment_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": r.id,
            "comment_id": r.comment_id,
            "user_id": r.user_id,
            "reply_to_user_id": r.reply_to_user_id,
            "content_type": r.content_type,
            "content": r.content,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in replies
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/delete")
async def delete_reply(req: ReplyDeleteRequest):
    db = get_db()
    user = require_login()
    await ReplyService.delete(db, user.id, req.reply_id)
    return BaseResponse(message="删除成功")
