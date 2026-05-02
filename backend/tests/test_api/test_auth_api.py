import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True))
async def test_login_register_new_user(client):
    response = await client.post("/api/auth/login", json={
        "email": "test_new@example.com",
        "code": "123456"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "test_new@example.com"


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True))
async def test_login_existing_user(client):
    # register first
    await client.post("/api/auth/login", json={
        "email": "existing@example.com",
        "code": "123456"
    })
    # login again
    response = await client.post("/api/auth/login", json={
        "email": "existing@example.com",
        "code": "123456"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "existing@example.com"


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=False))
async def test_login_wrong_code(client):
    response = await client.post("/api/auth/login", json={
        "email": "wrongcode@example.com",
        "code": "999999"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 1003


@pytest.mark.asyncio
async def test_me_without_auth(client):
    response = await client.post("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 2001


@pytest.mark.asyncio
@patch("app.services.auth_service.verify_code", new=AsyncMock(return_value=True))
async def test_me_with_auth(client):
    # login to get token
    login_resp = await client.post("/api/auth/login", json={
        "email": "me_test@example.com",
        "code": "123456"
    })
    token = login_resp.json()["data"]["token"]

    # call /me with token
    response = await client.post("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["email"] == "me_test@example.com"
