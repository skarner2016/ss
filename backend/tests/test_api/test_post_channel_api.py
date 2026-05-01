import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "u@test.com") -> str:
    resp = await client.post("/api/auth/login", json={"email": email, "password": "pass123"})
    return resp.json()["data"]["token"]


async def _create_channel(client: AsyncClient, name: str) -> int:
    resp = await client.post("/api/channel/create", json={"name": name})
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_post_with_channels(client: AsyncClient):
    token = await _register_and_login(client)
    ch_id = await _create_channel(client, "技术2")
    resp = await client.post(
        "/api/post/create",
        json={"title": "t", "content": "c", "channel_ids": [ch_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.json()["code"] == 0


@pytest.mark.asyncio
async def test_create_post_too_many_channels(client: AsyncClient):
    token = await _register_and_login(client, "u2@test.com")
    ids = [await _create_channel(client, f"ch{i}") for i in range(4)]
    resp = await client.post(
        "/api/post/create",
        json={"title": "t", "content": "c", "channel_ids": ids},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.json()["code"] == 6004


@pytest.mark.asyncio
async def test_post_detail_includes_channels(client: AsyncClient):
    token = await _register_and_login(client, "u3@test.com")
    ch_id = await _create_channel(client, "生活2")
    create_resp = await client.post(
        "/api/post/create",
        json={"title": "t", "content": "c", "channel_ids": [ch_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    post_id = create_resp.json()["data"]["id"]
    detail_resp = await client.post("/api/post/detail", json={"post_id": post_id})
    channels = detail_resp.json()["data"]["channels"]
    assert any(c["id"] == ch_id for c in channels)


@pytest.mark.asyncio
async def test_post_list_filter_by_channel(client: AsyncClient):
    token = await _register_and_login(client, "u4@test.com")
    ch_id = await _create_channel(client, "科技2")
    await client.post(
        "/api/post/create",
        json={"title": "in channel", "content": "c", "channel_ids": [ch_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/post/create",
        json={"title": "no channel", "content": "c", "channel_ids": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.post("/api/post/list", json={"channel_id": ch_id})
    titles = [p["title"] for p in resp.json()["data"]["items"]]
    assert "in channel" in titles
    assert "no channel" not in titles
