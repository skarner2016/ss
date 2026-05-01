from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode

db_session_var: ContextVar[AsyncSession] = ContextVar('db_session')
current_user_var: ContextVar[Optional['UserModel']] = ContextVar('current_user', default=None)


def get_db() -> AsyncSession:
    return db_session_var.get()


def get_current_user():
    return current_user_var.get()


def require_login():
    user = current_user_var.get()
    if user is None:
        raise ApiBusinessException(*ErrorCode.UNAUTHORIZED)
    return user
