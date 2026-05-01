import pytest
from pydantic import ValidationError
from app.schemas.post_schema import PostCreateRequest, PostUpdateRequest, PostListRequest


def test_post_create_channel_ids_default_empty():
    req = PostCreateRequest(title="t", content="c")
    assert req.channel_ids == []


def test_post_create_channel_ids_accepts_four():
    req = PostCreateRequest(title="t", content="c", channel_ids=[1, 2, 3, 4])
    assert len(req.channel_ids) == 4


def test_post_update_channel_ids_optional():
    req = PostUpdateRequest(post_id=1)
    assert req.channel_ids is None


def test_post_list_channel_id_optional():
    req = PostListRequest()
    assert req.channel_id is None
