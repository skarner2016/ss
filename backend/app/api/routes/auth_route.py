from fastapi import APIRouter
from app.schemas.auth_schema import SendCodeRequest, LoginRequest, UpdateMeRequest
from app.schemas.common_schema import BaseResponse
from app.services.auth_service import AuthService
from app.services.code_service import send_code
from app.core.context import get_db, require_login

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/send_code")
async def send_verification_code(req: SendCodeRequest):
    await send_code(req.email)
    return BaseResponse(data={"message": "ok"})


@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    token, user = await AuthService.login_or_register(db, req.email, req.code)
    return BaseResponse(data={
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
        }
    })


@router.post("/me")
async def me():
    user = require_login()
    return BaseResponse(data={
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
    })


@router.post("/user_info")
async def user_info(user_id: int):
    db = get_db()
    user = await AuthService.get_user_info(db, user_id)
    return BaseResponse(data={
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
    })


@router.post("/update_me")
async def update_me(req: UpdateMeRequest):
    db = get_db()
    user = require_login()
    updated = await AuthService.update_user_info(db, user.id, req.nickname, req.avatar_url, req.bio)
    return BaseResponse(data={
        "id": updated.id,
        "email": updated.email,
        "nickname": updated.nickname,
        "avatar_url": updated.avatar_url,
        "bio": updated.bio,
        "status": updated.status,
        "created_at": updated.created_at.isoformat(),
    })
