# Channel Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add channels to posts — a post belongs to up to 3 channels; users filter the post list by channel via top tabs.

**Architecture:** Independent `channels` table + `post_channels` join table. Channel CRUD APIs are unauthenticated. Post create/update/list/detail APIs are extended to support channels. Frontend adds channel tabs to PostList, badges to PostCard/PostDetail, and a multi-select to PostCreate/PostEdit.

**Tech Stack:** Python 3.12 + FastAPI + SQLAlchemy async (backend); Vue 3 + TypeScript + Element Plus + TanStack Query (frontend).

---

## File Map

### Backend — New Files
- `backend/app/models/channel_model.py` — `ChannelModel`, `PostChannelModel`
- `backend/app/schemas/channel_schema.py` — request/response schemas for channel endpoints
- `backend/app/services/channel_service.py` — channel CRUD + post-channel association logic
- `backend/app/api/routes/channel_route.py` — channel endpoints (`/api/channel/*`)

### Backend — Modified Files
- `backend/app/models/__init__.py` — export `ChannelModel`, `PostChannelModel`
- `backend/app/api/routes/__init__.py` — register `channel_router`
- `backend/app/schemas/post_schema.py` — add `channel_ids` to create/update/list requests
- `backend/app/api/routes/post_route.py` — pass `channel_ids` on write; batch-fetch channels on read
- `backend/app/services/post_service.py` — add `channel_id` filter to `get_list`
- `backend/app/core/error_codes.py` — add channel error codes

### Frontend — New Files
- `front/src/api/channel.ts` — `getPublicChannels()`

### Frontend — Modified Files
- `front/src/api/types.ts` — add `Channel` interface; extend `Post`, `PostListParams`, `PostCreateParams`, `PostUpdateParams`
- `front/src/pages/PostList.vue` — channel tabs + filtered query
- `front/src/components/PostCard.vue` — channel badges
- `front/src/pages/PostCreate.vue` — channel multi-select
- `front/src/pages/PostEdit.vue` — channel multi-select pre-filled
- `front/src/pages/PostDetail.vue` — channel badges

---

### Task 1: Channel Error Codes


**Files:**
- Modify: `backend/app/core/error_codes.py`

- [ ] **Step 1: Add channel error codes**

Open `backend/app/core/error_codes.py`. Add these lines before the `SYSTEM_ERROR` line:

```python
    # 频道错误 6xxx
    CHANNEL_NOT_FOUND = (6001, "频道不存在")
    CHANNEL_NAME_EXISTS = (6002, "频道名称已存在")
    CHANNEL_HAS_POSTS = (6003, "频道下存在帖子，无法删除")
    POST_CHANNEL_LIMIT = (6004, "每篇帖子最多关联3个频道")
    POST_CHANNEL_INVALID = (6005, "包含无效的频道ID")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/error_codes.py
git commit -m "feat: add channel error codes"
```

---

### Task 2: Channel Models

**Files:**
- Create: `backend/app/models/channel_model.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_channel_model.py`:

```python
import pytest
from app.models.channel_model import ChannelModel, PostChannelModel


def test_channel_model_tablename():
    assert ChannelModel.__tablename__ == "channels"


def test_post_channel_model_tablename():
    assert PostChannelModel.__tablename__ == "post_channels"


def test_channel_model_has_required_columns():
    cols = {c.key for c in ChannelModel.__table__.columns}
    assert {"id", "name", "description", "sort_order", "status", "created_at"} <= cols


def test_post_channel_model_has_required_columns():
    cols = {c.key for c in PostChannelModel.__table__.columns}
    assert {"post_id", "channel_id"} <= cols
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_channel_model.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.models.channel_model'`

- [ ] **Step 3: Create channel_model.py**

Create `backend/app/models/channel_model.py`:

```python
from datetime import datetime
from sqlalchemy import BigInteger, SmallInteger, String, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ChannelModel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(200))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PostChannelModel(Base):
    __tablename__ = "post_channels"
    __table_args__ = (
        UniqueConstraint("post_id", "channel_id", name="pk_post_channel"),
        Index("idx_channel_id", "channel_id"),
    )

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && uv run pytest tests/test_channel_model.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: Export from __init__.py**

Edit `backend/app/models/__init__.py` — replace entire file:

```python
from app.models.base import Base
from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.reply_model import ReplyModel
from app.models.like_model import LikeModel
from app.models.favorite_model import FavoriteModel
from app.models.channel_model import ChannelModel, PostChannelModel

__all__ = [
    "Base",
    "UserModel",
    "PostModel",
    "CommentModel",
    "ReplyModel",
    "LikeModel",
    "FavoriteModel",
    "ChannelModel",
    "PostChannelModel",
]
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/channel_model.py backend/app/models/__init__.py backend/tests/test_channel_model.py
git commit -m "feat: add ChannelModel and PostChannelModel"
```

---

### Task 3: Channel Schemas

**Files:**
- Create: `backend/app/schemas/channel_schema.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_channel_schema.py`:

```python
import pytest
from pydantic import ValidationError
from app.schemas.channel_schema import (
    ChannelCreateRequest, ChannelUpdateRequest, ChannelDeleteRequest,
    ChannelListRequest,
)


def test_channel_create_requires_name():
    with pytest.raises(ValidationError):
        ChannelCreateRequest()


def test_channel_create_name_max_length():
    with pytest.raises(ValidationError):
        ChannelCreateRequest(name="x" * 51)


def test_channel_create_valid():
    req = ChannelCreateRequest(name="技术", description="技术讨论", sort_order=1)
    assert req.name == "技术"
    assert req.sort_order == 1


def test_channel_update_requires_channel_id():
    with pytest.raises(ValidationError):
        ChannelUpdateRequest()


def test_channel_list_defaults():
    req = ChannelListRequest()
    assert req.page == 1
    assert req.page_size == 20
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_channel_schema.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create channel_schema.py**

Create `backend/app/schemas/channel_schema.py`:

```python
from pydantic import BaseModel, Field


class ChannelCreateRequest(BaseModel):
    name: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=200)
    sort_order: int = Field(default=0)


class ChannelUpdateRequest(BaseModel):
    channel_id: int
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    sort_order: int | None = None
    status: int | None = None


class ChannelDeleteRequest(BaseModel):
    channel_id: int


class ChannelListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && uv run pytest tests/test_channel_schema.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/channel_schema.py backend/tests/test_channel_schema.py
git commit -m "feat: add channel request schemas"
```

---

### Task 4: Channel Service

**Files:**
- Create: `backend/app/services/channel_service.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_channel_service.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.channel_service import ChannelService
from app.core.exceptions import ApiBusinessException


@pytest.mark.asyncio
async def test_create_channel_success():
    db = AsyncMock()
    db.flush = AsyncMock()
    with patch("app.services.channel_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)
        channel = await ChannelService.create(db, name="技术", description=None, sort_order=0)
        assert channel.name == "技术"
        db.add.assert_called_once()
        db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_create_channel_duplicate_name_raises():
    db = AsyncMock()
    with patch("app.services.channel_service.select"):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # existing channel
        db.execute = AsyncMock(return_value=mock_result)
        with pytest.raises(ApiBusinessException) as exc_info:
            await ChannelService.create(db, name="技术", description=None, sort_order=0)
        assert exc_info.value.code == 6002


@pytest.mark.asyncio
async def test_validate_channel_ids_too_many_raises():
    db = AsyncMock()
    with pytest.raises(ApiBusinessException) as exc_info:
        await ChannelService.validate_channel_ids(db, [1, 2, 3, 4])
    assert exc_info.value.code == 6004


@pytest.mark.asyncio
async def test_validate_channel_ids_invalid_id_raises():
    db = AsyncMock()
    with patch("app.services.channel_service.select"):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MagicMock(id=1)]  # only 1 found, 2 requested
        db.execute = AsyncMock(return_value=mock_result)
        with pytest.raises(ApiBusinessException) as exc_info:
            await ChannelService.validate_channel_ids(db, [1, 99])
        assert exc_info.value.code == 6005
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_channel_service.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create channel_service.py**

Create `backend/app/services/channel_service.py`:

```python
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel_model import ChannelModel, PostChannelModel
from app.core.exceptions import ApiBusinessException
from app.core.error_codes import ErrorCode


class ChannelService:
    @staticmethod
    async def create(db: AsyncSession, name: str, description: str | None, sort_order: int) -> ChannelModel:
        existing = await db.execute(select(ChannelModel).where(ChannelModel.name == name))
        if existing.scalar_one_or_none() is not None:
            raise ApiBusinessException(*ErrorCode.CHANNEL_NAME_EXISTS)
        channel = ChannelModel(
            name=name,
            description=description,
            sort_order=sort_order,
            status=1,
            created_at=datetime.now(timezone.utc),
        )
        db.add(channel)
        await db.flush()
        return channel

    @staticmethod
    async def get_or_raise(db: AsyncSession, channel_id: int) -> ChannelModel:
        result = await db.execute(select(ChannelModel).where(ChannelModel.id == channel_id))
        channel = result.scalar_one_or_none()
        if channel is None:
            raise ApiBusinessException(*ErrorCode.CHANNEL_NOT_FOUND)
        return channel

    @staticmethod
    async def update(db: AsyncSession, channel_id: int, name: str | None, description: str | None,
                     sort_order: int | None, status: int | None) -> ChannelModel:
        channel = await ChannelService.get_or_raise(db, channel_id)
        if name is not None and name != channel.name:
            existing = await db.execute(select(ChannelModel).where(ChannelModel.name == name))
            if existing.scalar_one_or_none() is not None:
                raise ApiBusinessException(*ErrorCode.CHANNEL_NAME_EXISTS)
            channel.name = name
        if description is not None:
            channel.description = description
        if sort_order is not None:
            channel.sort_order = sort_order
        if status is not None:
            channel.status = status
        await db.flush()
        return channel

    @staticmethod
    async def delete(db: AsyncSession, channel_id: int):
        channel = await ChannelService.get_or_raise(db, channel_id)
        count_result = await db.execute(
            select(func.count()).select_from(PostChannelModel).where(PostChannelModel.channel_id == channel_id)
        )
        if count_result.scalar() > 0:
            raise ApiBusinessException(*ErrorCode.CHANNEL_HAS_POSTS)
        await db.delete(channel)
        await db.flush()

    @staticmethod
    async def get_list(db: AsyncSession, page: int, page_size: int) -> tuple[list[ChannelModel], int]:
        total_result = await db.execute(select(func.count()).select_from(ChannelModel))
        total = total_result.scalar()
        result = await db.execute(
            select(ChannelModel)
            .order_by(ChannelModel.sort_order.asc(), ChannelModel.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def get_public_list(db: AsyncSession) -> list[ChannelModel]:
        result = await db.execute(
            select(ChannelModel)
            .where(ChannelModel.status == 1)
            .order_by(ChannelModel.sort_order.asc(), ChannelModel.id.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def validate_channel_ids(db: AsyncSession, channel_ids: list[int]) -> None:
        if len(channel_ids) > 3:
            raise ApiBusinessException(*ErrorCode.POST_CHANNEL_LIMIT)
        if not channel_ids:
            return
        result = await db.execute(
            select(ChannelModel).where(ChannelModel.id.in_(channel_ids))
        )
        found = result.scalars().all()
        if len(found) != len(channel_ids):
            raise ApiBusinessException(*ErrorCode.POST_CHANNEL_INVALID)

    @staticmethod
    async def set_post_channels(db: AsyncSession, post_id: int, channel_ids: list[int]) -> None:
        await db.execute(
            PostChannelModel.__table__.delete().where(PostChannelModel.post_id == post_id)
        )
        for cid in channel_ids:
            db.add(PostChannelModel(post_id=post_id, channel_id=cid))
        await db.flush()

    @staticmethod
    async def get_channels_for_posts(db: AsyncSession, post_ids: list[int]) -> dict[int, list[dict]]:
        if not post_ids:
            return {}
        result = await db.execute(
            select(PostChannelModel.post_id, ChannelModel.id, ChannelModel.name)
            .join(ChannelModel, ChannelModel.id == PostChannelModel.channel_id)
            .where(PostChannelModel.post_id.in_(post_ids))
        )
        mapping: dict[int, list[dict]] = {pid: [] for pid in post_ids}
        for row in result.all():
            mapping[row.post_id].append({"id": row.id, "name": row.name})
        return mapping
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && uv run pytest tests/test_channel_service.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/channel_service.py backend/tests/test_channel_service.py
git commit -m "feat: add ChannelService with CRUD and post-channel association"
```

---

### Task 5: Channel Route

**Files:**
- Create: `backend/app/api/routes/channel_route.py`
- Modify: `backend/app/api/routes/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_api/test_channel_api.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_api/test_channel_api.py -v
```

Expected: FAIL with `404 Not Found` (route not registered)

- [ ] **Step 3: Create channel_route.py**

Create `backend/app/api/routes/channel_route.py`:

```python
from fastapi import APIRouter
from app.schemas.channel_schema import (
    ChannelCreateRequest, ChannelUpdateRequest, ChannelDeleteRequest, ChannelListRequest,
)
from app.schemas.common_schema import BaseResponse, PageData
from app.services.channel_service import ChannelService
from app.core.context import get_db

router = APIRouter(prefix="/api/channel", tags=["频道"])


@router.post("/create")
async def create_channel(req: ChannelCreateRequest):
    db = get_db()
    channel = await ChannelService.create(db, req.name, req.description, req.sort_order)
    return BaseResponse(data={"id": channel.id, "name": channel.name})


@router.post("/update")
async def update_channel(req: ChannelUpdateRequest):
    db = get_db()
    channel = await ChannelService.update(db, req.channel_id, req.name, req.description, req.sort_order, req.status)
    return BaseResponse(data={"id": channel.id, "name": channel.name, "status": channel.status})


@router.post("/delete")
async def delete_channel(req: ChannelDeleteRequest):
    db = get_db()
    await ChannelService.delete(db, req.channel_id)
    return BaseResponse(message="删除成功")


@router.post("/list")
async def list_channels(req: ChannelListRequest):
    db = get_db()
    channels, total = await ChannelService.get_list(db, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {"id": c.id, "name": c.name, "description": c.description,
         "sort_order": c.sort_order, "status": c.status}
        for c in channels
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/public_list")
async def public_list_channels():
    db = get_db()
    channels = await ChannelService.get_public_list(db)
    return BaseResponse(data=[
        {"id": c.id, "name": c.name, "sort_order": c.sort_order}
        for c in channels
    ])
```

- [ ] **Step 4: Register router in `backend/app/api/routes/__init__.py`**

Replace entire file:

```python
from fastapi import APIRouter
from app.api.routes.auth_route import router as auth_router
from app.api.routes.post_route import router as post_router
from app.api.routes.comment_route import router as comment_router
from app.api.routes.reply_route import router as reply_router
from app.api.routes.like_route import router as like_router
from app.api.routes.favorite_route import router as favorite_router
from app.api.routes.channel_route import router as channel_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(post_router)
api_router.include_router(comment_router)
api_router.include_router(reply_router)
api_router.include_router(like_router)
api_router.include_router(favorite_router)
api_router.include_router(channel_router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_api/test_channel_api.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/routes/channel_route.py backend/app/api/routes/__init__.py backend/tests/test_api/test_channel_api.py
git commit -m "feat: add channel API endpoints"
```

---

### Task 6: Extend Post Schemas and Service for Channels

**Files:**
- Modify: `backend/app/schemas/post_schema.py`
- Modify: `backend/app/services/post_service.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_post_channel_schema.py`:

```python
import pytest
from pydantic import ValidationError
from app.schemas.post_schema import PostCreateRequest, PostUpdateRequest, PostListRequest


def test_post_create_channel_ids_default_empty():
    req = PostCreateRequest(title="t", content="c")
    assert req.channel_ids == []


def test_post_create_channel_ids_max_3():
    with pytest.raises(ValidationError):
        PostCreateRequest(title="t", content="c", channel_ids=[1, 2, 3, 4])


def test_post_update_channel_ids_optional():
    req = PostUpdateRequest(post_id=1)
    assert req.channel_ids is None


def test_post_list_channel_id_optional():
    req = PostListRequest()
    assert req.channel_id is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_post_channel_schema.py -v
```

Expected: FAIL — `PostCreateRequest` has no `channel_ids` field

- [ ] **Step 3: Update `backend/app/schemas/post_schema.py`**

Replace entire file:

```python
from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(min_length=1)
    channel_ids: list[int] = Field(default_factory=list, max_length=3)


class PostUpdateRequest(BaseModel):
    post_id: int
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    channel_ids: list[int] | None = None


class PostDeleteRequest(BaseModel):
    post_id: int


class PostListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    channel_id: int | None = None


class PostDetailRequest(BaseModel):
    post_id: int


class PostInfo(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    like_count: int
    comment_count: int
    status: int
    created_at: str
    updated_at: str
```

- [ ] **Step 4: Update `backend/app/services/post_service.py`** — add `channel_id` filter to `get_list`

Replace the `get_list` static method (the entire method body, lines 35–48 in the original file):

```python
    @staticmethod
    async def get_list(db: AsyncSession, page: int, page_size: int, channel_id: int | None = None) -> tuple[list[PostModel], int]:
        from app.models.channel_model import PostChannelModel
        base_filter = PostModel.deleted_at.is_(None)

        if channel_id is not None:
            count_stmt = (
                select(func.count())
                .select_from(PostModel)
                .join(PostChannelModel, PostChannelModel.post_id == PostModel.id)
                .where(base_filter, PostChannelModel.channel_id == channel_id)
            )
            list_stmt = (
                select(PostModel)
                .join(PostChannelModel, PostChannelModel.post_id == PostModel.id)
                .where(base_filter, PostChannelModel.channel_id == channel_id)
                .order_by(PostModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        else:
            count_stmt = select(func.count()).select_from(PostModel).where(base_filter)
            list_stmt = (
                select(PostModel)
                .where(base_filter)
                .order_by(PostModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )

        total = (await db.execute(count_stmt)).scalar()
        posts = (await db.execute(list_stmt)).scalars().all()
        return posts, total
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_post_channel_schema.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/post_schema.py backend/app/services/post_service.py backend/tests/test_post_channel_schema.py
git commit -m "feat: extend post schema and service for channel filtering"
```

---

### Task 7: Wire Channels into Post Route

**Files:**
- Modify: `backend/app/api/routes/post_route.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_api/test_post_channel_api.py`:

```python
import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "u@test.com") -> str:
    await client.post("/api/auth/register", json={"email": email, "password": "pass123"})
    resp = await client.post("/api/auth/login", json={"email": email, "password": "pass123"})
    return resp.json()["data"]["token"]


async def _create_channel(client: AsyncClient, name: str) -> int:
    resp = await client.post("/api/channel/create", json={"name": name})
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_post_with_channels(client: AsyncClient):
    token = await _register_and_login(client)
    ch_id = await _create_channel(client, "技术")
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
    ch_id = await _create_channel(client, "生活")
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
    ch_id = await _create_channel(client, "科技")
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_api/test_post_channel_api.py -v
```

Expected: FAIL — post create ignores `channel_ids`, detail has no `channels` field

- [ ] **Step 3: Update `backend/app/api/routes/post_route.py`**

Replace entire file:

```python
from fastapi import APIRouter
from sqlalchemy import select
from app.schemas.post_schema import (
    PostCreateRequest, PostUpdateRequest, PostDeleteRequest,
    PostListRequest, PostDetailRequest
)
from app.schemas.common_schema import BaseResponse, PageData
from app.services.post_service import PostService
from app.services.channel_service import ChannelService
from app.models.user_model import UserModel
from app.models.like_model import LikeModel
from app.models.favorite_model import FavoriteModel
from app.core.context import get_db, require_login, get_current_user

router = APIRouter(prefix="/api/post", tags=["帖子"])


@router.post("/create")
async def create_post(req: PostCreateRequest):
    db = get_db()
    user = require_login()
    if req.channel_ids:
        await ChannelService.validate_channel_ids(db, req.channel_ids)
    post = await PostService.create(db, user.id, req.title, req.content)
    if req.channel_ids:
        await ChannelService.set_post_channels(db, post.id, req.channel_ids)
    return BaseResponse(data={"id": post.id, "title": post.title, "content": post.content})


@router.post("/detail")
async def post_detail(req: PostDetailRequest):
    db = get_db()
    post = await PostService.get_detail(db, req.post_id)

    author_result = await db.execute(select(UserModel).where(UserModel.id == post.user_id))
    author = author_result.scalar_one_or_none()

    is_liked = False
    is_favorited = False
    user = get_current_user()
    if user:
        like_result = await db.execute(
            select(LikeModel).where(
                LikeModel.user_id == user.id,
                LikeModel.target_type == 1,
                LikeModel.target_id == post.id,
            )
        )
        is_liked = like_result.scalar_one_or_none() is not None

        fav_result = await db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user.id,
                FavoriteModel.post_id == post.id,
            )
        )
        is_favorited = fav_result.scalar_one_or_none() is not None

    channels_map = await ChannelService.get_channels_for_posts(db, [post.id])

    return BaseResponse(data={
        "id": post.id,
        "user_id": post.user_id,
        "author_nickname": author.nickname if author else None,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "status": post.status,
        "is_liked": is_liked,
        "is_favorited": is_favorited,
        "channels": channels_map.get(post.id, []),
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    })


@router.post("/list")
async def post_list(req: PostListRequest):
    db = get_db()
    posts, total = await PostService.get_list(db, req.page, req.page_size, req.channel_id)
    total_pages = (total + req.page_size - 1) // req.page_size

    user_ids = list({p.user_id for p in posts})
    user_map: dict[int, str | None] = {}
    if user_ids:
        user_result = await db.execute(select(UserModel.id, UserModel.nickname).where(UserModel.id.in_(user_ids)))
        for row in user_result.all():
            user_map[row.id] = row.nickname

    liked_ids: set[int] = set()
    favorited_ids: set[int] = set()
    current_user = get_current_user()
    if current_user and posts:
        post_ids = [p.id for p in posts]
        like_result = await db.execute(
            select(LikeModel.target_id).where(
                LikeModel.user_id == current_user.id,
                LikeModel.target_type == 1,
                LikeModel.target_id.in_(post_ids),
            )
        )
        liked_ids = {row[0] for row in like_result.all()}

        fav_result = await db.execute(
            select(FavoriteModel.post_id).where(
                FavoriteModel.user_id == current_user.id,
                FavoriteModel.post_id.in_(post_ids),
            )
        )
        favorited_ids = {row[0] for row in fav_result.all()}

    post_ids = [p.id for p in posts]
    channels_map = await ChannelService.get_channels_for_posts(db, post_ids)

    items = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "author_nickname": user_map.get(p.user_id),
            "title": p.title,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "is_liked": p.id in liked_ids,
            "is_favorited": p.id in favorited_ids,
            "channels": channels_map.get(p.id, []),
            "created_at": p.created_at.isoformat(),
        }
        for p in posts
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/update")
async def update_post(req: PostUpdateRequest):
    db = get_db()
    user = require_login()
    if req.channel_ids is not None:
        await ChannelService.validate_channel_ids(db, req.channel_ids)
    post = await PostService.update(db, user.id, req.post_id, req.title, req.content)
    if req.channel_ids is not None:
        await ChannelService.set_post_channels(db, post.id, req.channel_ids)
    return BaseResponse(data={"id": post.id, "title": post.title, "content": post.content})


@router.post("/delete")
async def delete_post(req: PostDeleteRequest):
    db = get_db()
    user = require_login()
    await PostService.delete(db, user.id, req.post_id)
    return BaseResponse(message="删除成功")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_api/test_post_channel_api.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: Run full backend test suite**

```bash
cd backend && uv run pytest -v
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/routes/post_route.py backend/tests/test_api/test_post_channel_api.py
git commit -m "feat: wire channel_ids into post create/update/list/detail"
```

---

### Task 8: Frontend Types and Channel API Client

**Files:**
- Modify: `front/src/api/types.ts`
- Create: `front/src/api/channel.ts`

- [ ] **Step 1: Add `Channel` interface and extend existing types in `front/src/api/types.ts`**

Add after the `Favorite` interface block and update `Post`, `PostListParams`, `PostCreateParams`, `PostUpdateParams`:

```typescript
// Channel
export interface Channel {
  id: number
  name: string
  sort_order: number
}
```

Update `Post` interface — add `channels` field:

```typescript
export interface Post {
  id: number
  user_id: number
  author_nickname?: string | null
  title: string
  content?: string
  like_count: number
  comment_count: number
  status: number
  created_at: string
  updated_at?: string
  is_liked?: boolean
  is_favorited?: boolean
  channels?: Channel[]
}
```

Update `PostListParams`:

```typescript
export interface PostListParams {
  page: number
  page_size: number
  channel_id?: number | null
}
```

Update `PostCreateParams`:

```typescript
export interface PostCreateParams {
  title: string
  content: string
  channel_ids?: number[]
}
```

Update `PostUpdateParams`:

```typescript
export interface PostUpdateParams {
  post_id: number
  title?: string
  content?: string
  channel_ids?: number[] | null
}
```

- [ ] **Step 2: Create `front/src/api/channel.ts`**

```typescript
import request from './request'
import type { ApiResponse, Channel } from './types'

export function getPublicChannels(): Promise<Channel[]> {
  return request.post<ApiResponse<Channel[]>>('/channel/public_list', {}).then((r) => r.data.data)
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd front && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add front/src/api/types.ts front/src/api/channel.ts
git commit -m "feat: add Channel type and getPublicChannels API client"
```

---

### Task 9: PostList.vue — Channel Tabs

**Files:**
- Modify: `front/src/pages/PostList.vue`

- [ ] **Step 1: Replace `front/src/pages/PostList.vue`**

```vue
<template>
  <div class="post-list">
    <el-tabs v-model="selectedChannelId" class="channel-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane
        v-for="ch in channels"
        :key="ch.id"
        :label="ch.name"
        :name="String(ch.id)"
      />
    </el-tabs>

    <div v-if="flattenPosts.length === 0 && !isLoading" class="empty-state">
      <el-empty description="暂无帖子" />
    </div>
    <PostCard
      v-for="post in flattenPosts"
      :key="post.id"
      :post="post"
    />
    <div v-if="isLoading" class="loading-more">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
    <div v-else-if="hasMore" class="load-more" ref="loadMoreRef">
      <el-button text @click="() => fetchNextPage()">加载更多</el-button>
    </div>
    <div v-else-if="flattenPosts.length > 0" class="no-more">
      没有更多了
    </div>

    <el-button
      v-if="authStore.isLoggedIn"
      type="primary"
      circle
      class="fab-button"
      @click="router.push('/post/create')"
    >
      <el-icon><EditPen /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import { Loading, EditPen } from '@element-plus/icons-vue'
import { getPostList } from '@/api/post'
import { getPublicChannels } from '@/api/channel'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// "all" means no filter; numeric string means channel id
const selectedChannelId = ref<string>(
  route.query.channel_id ? String(route.query.channel_id) : 'all'
)

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const activeChannelId = computed<number | null>(() => {
  if (selectedChannelId.value === 'all') return null
  return Number(selectedChannelId.value)
})

const { data, isLoading, fetchNextPage, hasNextPage, refetch } = useInfiniteQuery({
  queryKey: ['posts', activeChannelId],
  queryFn: ({ pageParam = 1 }) =>
    getPostList({ page: pageParam, page_size: 20, channel_id: activeChannelId.value }),
  getNextPageParam: (lastPage) =>
    lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  initialPageParam: 1,
})

function handleTabChange(name: string) {
  selectedChannelId.value = name
  if (name === 'all') {
    router.replace({ query: {} })
  } else {
    router.replace({ query: { channel_id: name } })
  }
}

const flattenPosts = computed(() => data.value?.pages.flatMap((page) => page.items) ?? [])
const hasMore = computed(() => hasNextPage.value ?? false)
const loadMoreRef = ref<HTMLElement>()
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
        fetchNextPage()
      }
    },
    { threshold: 0.1 },
  )
  if (loadMoreRef.value) observer.observe(loadMoreRef.value)
})

onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.post-list {
  position: relative;
}

.channel-tabs {
  margin-bottom: 12px;
}

.loading-more, .no-more, .load-more {
  text-align: center;
  padding: 16px;
  color: #909399;
}

.fab-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 56px;
  height: 56px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd front && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add front/src/pages/PostList.vue
git commit -m "feat: add channel tabs to PostList"
```

---

### Task 10: PostCard.vue — Channel Badges

**Files:**
- Modify: `front/src/components/PostCard.vue`

- [ ] **Step 1: Replace `front/src/components/PostCard.vue`**

```vue
<template>
  <el-card class="post-card" shadow="hover" @click="router.push(`/post/${post.id}`)">
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-meta">
      <span class="post-author">{{ post.author_nickname || '用户 #' + post.user_id }}</span>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </p>
    <div v-if="post.channels && post.channels.length > 0" class="post-channels" @click.stop>
      <el-tag
        v-for="ch in post.channels"
        :key="ch.id"
        size="small"
        type="info"
        class="channel-tag"
        @click="router.push({ path: '/', query: { channel_id: ch.id } })"
      >{{ ch.name }}</el-tag>
    </div>
    <div class="post-stats" @click.stop>
      <LikeButton
        :target-id="post.id"
        :target-type="1"
        :liked="post.is_liked ?? false"
        :count="post.like_count"
        :query-key="props.queryKey ?? ['posts']"
      />
      <FavoriteButton
        :post-id="post.id"
        :favorited="post.is_favorited ?? false"
        :query-key="props.queryKey ?? ['posts']"
      />
      <span class="stat-item">
        <el-icon><ChatDotRound /></el-icon>
        {{ post.comment_count }}
      </span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import type { Post } from '@/api/types'
import { formatTime } from '@/utils/time'
import LikeButton from '@/components/LikeButton.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'

const props = defineProps<{ post: Post; queryKey?: string[] }>()

const router = useRouter()
</script>

<style scoped>
.post-card {
  cursor: pointer;
  margin-bottom: 12px;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
}

.post-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.post-meta {
  color: #909399;
  font-size: 13px;
  margin: 0 0 8px 0;
  display: flex;
  gap: 12px;
}

.post-channels {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.channel-tag {
  cursor: pointer;
}

.post-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd front && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add front/src/components/PostCard.vue
git commit -m "feat: add channel badges to PostCard"
```

---

### Task 11: PostCreate.vue and PostEdit.vue — Channel Multi-Select

**Files:**
- Modify: `front/src/pages/PostCreate.vue`
- Modify: `front/src/pages/PostEdit.vue`

- [ ] **Step 1: Replace `front/src/pages/PostCreate.vue`**

```vue
<template>
  <div class="post-create">
    <h2>发帖</h2>
    <el-form @submit.prevent="handleSubmit">
      <el-form-item>
        <el-input v-model="title" placeholder="标题" maxlength="200" show-word-limit size="large" />
      </el-form-item>
      <el-form-item>
        <MdEditor
          v-model="content"
          :style="{ height: '400px' }"
          placeholder="输入内容（支持 Markdown）..."
        />
      </el-form-item>
      <el-form-item label="频道">
        <el-select
          v-model="channelIds"
          multiple
          placeholder="选择频道（最多3个）"
          style="width: 100%"
        >
          <el-option
            v-for="ch in channels"
            :key="ch.id"
            :label="ch.name"
            :value="ch.id"
            :disabled="channelIds.length >= 3 && !channelIds.includes(ch.id)"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit">发布</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMutation, useQueryClient, useQuery } from '@tanstack/vue-query'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { createPost } from '@/api/post'
import { getPublicChannels } from '@/api/channel'

const router = useRouter()
const queryClient = useQueryClient()

const title = ref('')
const content = ref('')
const channelIds = ref<number[]>([])
const loading = ref(false)

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const createMutation = useMutation({
  mutationFn: createPost,
  onSuccess: (data) => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push(`/post/${data.id}`)
  },
  onError: (err: any) => {
    ElMessage.error(err?.message ?? '发布失败')
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await createMutation.mutateAsync({
      title: title.value,
      content: content.value,
      channel_ids: channelIds.value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-create {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-create h2 {
  margin-bottom: 20px;
}
</style>
```

- [ ] **Step 2: Replace `front/src/pages/PostEdit.vue`**

```vue
<template>
  <div v-if="post" class="post-edit">
    <h2>编辑帖子</h2>
    <el-form @submit.prevent="handleSubmit">
      <el-form-item>
        <el-input v-model="title" placeholder="标题" maxlength="200" show-word-limit size="large" />
      </el-form-item>
      <el-form-item>
        <MdEditor
          v-model="content"
          :style="{ height: '400px' }"
          placeholder="输入内容（支持 Markdown）..."
        />
      </el-form-item>
      <el-form-item label="频道">
        <el-select
          v-model="channelIds"
          multiple
          placeholder="选择频道（最多3个）"
          style="width: 100%"
        >
          <el-option
            v-for="ch in channels"
            :key="ch.id"
            :label="ch.name"
            :value="ch.id"
            :disabled="channelIds.length >= 3 && !channelIds.includes(ch.id)"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit">保存</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
  <div v-else class="loading">
    <el-icon class="is-loading"><Loading /></el-icon>
    加载中...
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getPostDetail, updatePost } from '@/api/post'
import { getPublicChannels } from '@/api/channel'

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const postId = computed(() => Number(route.params.id))

const { data: post } = useQuery({
  queryKey: ['post', postId.value],
  queryFn: () => getPostDetail(postId.value),
})

const { data: channelData } = useQuery({
  queryKey: ['channels'],
  queryFn: getPublicChannels,
})
const channels = computed(() => channelData.value ?? [])

const title = ref('')
const content = ref('')
const channelIds = ref<number[]>([])
const loading = ref(false)

watch(post, (p) => {
  if (p) {
    title.value = p.title
    content.value = p.content || ''
    channelIds.value = p.channels?.map((c) => c.id) ?? []
  }
}, { immediate: true })

const updateMutation = useMutation({
  mutationFn: updatePost,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['post', postId.value] })
    router.push(`/post/${postId.value}`)
  },
  onError: (err: any) => {
    ElMessage.error(err?.message ?? '保存失败')
  },
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  loading.value = true
  try {
    await updateMutation.mutateAsync({
      post_id: postId.value,
      title: title.value,
      content: content.value,
      channel_ids: channelIds.value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-edit {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.post-edit h2 {
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd front && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add front/src/pages/PostCreate.vue front/src/pages/PostEdit.vue
git commit -m "feat: add channel multi-select to PostCreate and PostEdit"
```

---

### Task 12: PostDetail.vue — Channel Badges

**Files:**
- Modify: `front/src/pages/PostDetail.vue`

- [ ] **Step 1: Add channel badges to `front/src/pages/PostDetail.vue`**

In the `<template>`, add the channel badges block after the `.post-meta` div and before `.post-content`:

```vue
    <div v-if="post.channels && post.channels.length > 0" class="post-channels">
      <el-tag
        v-for="ch in post.channels"
        :key="ch.id"
        size="small"
        type="info"
        class="channel-tag"
        @click="router.push({ path: '/', query: { channel_id: ch.id } })"
      >{{ ch.name }}</el-tag>
    </div>
```

In the `<style scoped>` block, add:

```css
.post-channels {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.channel-tag {
  cursor: pointer;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd front && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3: Run full frontend build**

```bash
cd front && npm run build
```

Expected: build succeeds with no errors

- [ ] **Step 4: Commit**

```bash
git add front/src/pages/PostDetail.vue
git commit -m "feat: add channel badges to PostDetail"
```
