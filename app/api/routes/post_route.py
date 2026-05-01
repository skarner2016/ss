from fastapi import APIRouter
from app.schemas.post_schema import (
    PostCreateRequest, PostUpdateRequest, PostDeleteRequest,
    PostListRequest, PostDetailRequest
)
from app.schemas.common_schema import BaseResponse, PageData
from app.services.post_service import PostService
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/post", tags=["帖子"])


@router.post("/create")
async def create_post(req: PostCreateRequest):
    db = get_db()
    user = require_login()
    post = await PostService.create(db, user.id, req.title, req.content)
    return BaseResponse(data={
        "id": post.id,
        "title": post.title,
        "content": post.content,
    })


@router.post("/detail")
async def post_detail(req: PostDetailRequest):
    db = get_db()
    post = await PostService.get_detail(db, req.post_id)
    return BaseResponse(data={
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "status": post.status,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    })


@router.post("/list")
async def post_list(req: PostListRequest):
    db = get_db()
    posts, total = await PostService.get_list(db, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "title": p.title,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at.isoformat(),
        }
        for p in posts
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/update")
async def update_post(req: PostUpdateRequest):
    db = get_db()
    user = require_login()
    post = await PostService.update(db, user.id, req.post_id, req.title, req.content)
    return BaseResponse(data={
        "id": post.id,
        "title": post.title,
        "content": post.content,
    })


@router.post("/delete")
async def delete_post(req: PostDeleteRequest):
    db = get_db()
    user = require_login()
    await PostService.delete(db, user.id, req.post_id)
    return BaseResponse(message="删除成功")
