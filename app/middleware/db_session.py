from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.database import async_session_factory
from app.core.context import db_session_var


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with async_session_factory() as session:
            token = db_session_var.set(session)
            try:
                response = await call_next(request)
                return response
            finally:
                db_session_var.reset(token)
                await session.close()
