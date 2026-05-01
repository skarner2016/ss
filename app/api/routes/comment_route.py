from fastapi import APIRouter
from app.schemas.comment_schema import CommentCreateRequest, CommentDeleteRequest, CommentListRequest
from app.schemas.common_schema import BaseResponse, PageData
from app.services.comment_service import CommentService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/comment", tags=["评论"])


@router.post("/create")
async def create_comment(req: CommentCreateRequest):
    db = get_db()
    user = require_login()
    comment = await CommentService.create(db, user.id, req.post_id, req.content)
    return BaseResponse(data={
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
    })


@router.post("/list")
async def comment_list(req: CommentListRequest):
    db = get_db()
    comments, total = await CommentService.get_list(db, req.post_id, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": c.id,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "content_type": c.content_type,
            "content": c.content,
            "reply_count": c.reply_count,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/delete")
async def delete_comment(req: CommentDeleteRequest):
    db = get_db()
    user = require_login()
    await CommentService.delete(db, user.id, req.comment_id)
    return BaseResponse(message="删除成功")
