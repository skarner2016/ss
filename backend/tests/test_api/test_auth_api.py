import pytest


@pytest.mark.asyncio
async def test_login_register_new_user(client):
    response = await client.post("/api/auth/login", json={
        "email": "test_new@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "test_new@example.com"


@pytest.mark.asyncio
async def test_login_existing_user(client):
    # register first
    await client.post("/api/auth/login", json={
        "email": "existing@example.com",
        "password": "password123"
    })
    # login again
    response = await client.post("/api/auth/login", json={
        "email": "existing@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "existing@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    # register first
    await client.post("/api/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "password123"
    })
    # login with wrong password
    response = await client.post("/api/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 2002
    assert data["message"] == "密码错误"


@pytest.mark.asyncio
async def test_me_without_auth(client):
    response = await client.post("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 2001


@pytest.mark.asyncio
async def test_me_with_auth(client):
    # login to get token
    login_resp = await client.post("/api/auth/login", json={
        "email": "me_test@example.com",
        "password": "password123"
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
