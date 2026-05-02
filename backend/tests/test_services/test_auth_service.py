import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.auth_service import AuthService
from app.core.exceptions import ApiBusinessException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=False))
async def test_login_with_invalid_code(mock_db):
    with pytest.raises(ApiBusinessException) as exc_info:
        await AuthService.login_or_register(mock_db, "test@example.com", "000000")
    assert exc_info.value.code == 1003


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True))
async def test_register_new_user(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    token, user = await AuthService.login_or_register(mock_db, "new@test.com", "123456")
    assert isinstance(token, str)
    assert user.email == "new@test.com"
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True))
async def test_login_existing_user(mock_db):
    from app.models.user_model import UserModel
    fake_user = UserModel(
        id=1,
        email="exist@test.com",
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

    token, user = await AuthService.login_or_register(mock_db, "exist@test.com", "123456")
    assert isinstance(token, str)
    assert user.id == 1
