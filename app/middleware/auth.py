from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import select
from app.core.context import db_session_var, current_user_var
from app.core.security import decode_token
from app.models.user_model import UserModel


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        if token:
            payload = decode_token(token)
            if payload and "user_id" in payload:
                db = db_session_var.get()
                result = await db.execute(
                    select(UserModel).where(UserModel.id == payload["user_id"])
                )
                user = result.scalar_one_or_none()
                if user and user.status == 1:
                    current_user_var.set(user)

        try:
            response = await call_next(request)
            return response
        finally:
            current_user_var.set(None)
