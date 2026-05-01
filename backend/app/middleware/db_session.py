from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import app.core.database as _db
from app.core.context import db_session_var


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with _db.async_session_factory() as session:
            token = db_session_var.set(session)
            try:
                response = await call_next(request)
                if response.status_code < 400:
                    await session.commit()
                else:
                    await session.rollback()
                return response
            finally:
                db_session_var.reset(token)
                await session.close()
