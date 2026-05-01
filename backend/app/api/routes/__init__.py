from fastapi import APIRouter
from app.api.routes.auth_route import router as auth_router
from app.api.routes.post_route import router as post_router
from app.api.routes.comment_route import router as comment_router
from app.api.routes.reply_route import router as reply_router
from app.api.routes.like_route import router as like_router
from app.api.routes.favorite_route import router as favorite_router
from app.api.routes.channel_route import router as channel_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(post_router)
api_router.include_router(comment_router)
api_router.include_router(reply_router)
api_router.include_router(like_router)
api_router.include_router(favorite_router)
api_router.include_router(channel_router)
