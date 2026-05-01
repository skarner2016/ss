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
