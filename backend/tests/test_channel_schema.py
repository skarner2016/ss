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
