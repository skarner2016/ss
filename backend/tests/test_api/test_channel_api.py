import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_channel(client: AsyncClient):
    resp = await client.post("/api/channel/create", json={"name": "技术"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["name"] == "技术"


@pytest.mark.asyncio
async def test_create_channel_duplicate_name(client: AsyncClient):
    await client.post("/api/channel/create", json={"name": "生活"})
    resp = await client.post("/api/channel/create", json={"name": "生活"})
    assert resp.json()["code"] == 6002


@pytest.mark.asyncio
async def test_public_list_returns_active_only(client: AsyncClient):
    await client.post("/api/channel/create", json={"name": "活跃频道", "sort_order": 0})
    resp = await client.post("/api/channel/create", json={"name": "禁用频道", "sort_order": 1})
    channel_id = resp.json()["data"]["id"]
    await client.post("/api/channel/update", json={"channel_id": channel_id, "status": 0})

    resp = await client.post("/api/channel/public_list", json={})
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()["data"]]
    assert "活跃频道" in names
    assert "禁用频道" not in names


@pytest.mark.asyncio
async def test_delete_channel_no_posts_succeeds(client: AsyncClient):
    resp = await client.post("/api/channel/create", json={"name": "待删频道"})
    channel_id = resp.json()["data"]["id"]
    del_resp = await client.post("/api/channel/delete", json={"channel_id": channel_id})
    assert del_resp.json()["code"] == 0
