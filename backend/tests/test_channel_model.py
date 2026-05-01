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
