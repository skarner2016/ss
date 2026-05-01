import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.auth_service import AuthService
from app.core.exceptions import ApiBusinessException
from app.models.user_model import UserModel


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_register_new_user(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    token, user = await AuthService.login_or_register(mock_db, "new@test.com", "password123")
    assert isinstance(token, str)
    assert user.email == "new@test.com"
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_login_existing_user(mock_db):
    from app.core.security import hash_password
    fake_user = UserModel(
        id=1,
        email="exist@test.com",
        password_hash=hash_password("password123"),
        nickname=None,
        avatar_url=None,
        bio=None,
        status=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_db.execute.return_value = mock_result

    token, user = await AuthService.login_or_register(mock_db, "exist@test.com", "password123")
    assert isinstance(token, str)
    assert user.id == 1


@pytest.mark.asyncio
async def test_login_wrong_password(mock_db):
    from app.core.security import hash_password
    fake_user = UserModel(
        id=1,
        email="exist@test.com",
        password_hash=hash_password("password123"),
        nickname=None, avatar_url=None, bio=None,
        status=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_db.execute.return_value = mock_result

    with pytest.raises(ApiBusinessException) as exc_info:
        await AuthService.login_or_register(mock_db, "exist@test.com", "wrong-password")
    assert exc_info.value.code == 2002
