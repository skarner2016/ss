from pydantic import BaseModel, Field


class ReplyCreateRequest(BaseModel):
    comment_id: int
    reply_to_user_id: int | None = None
    content: str = Field(min_length=1)


class ReplyDeleteRequest(BaseModel):
    reply_id: int


class ReplyListRequest(BaseModel):
    comment_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ReplyInfo(BaseModel):
    id: int
    comment_id: int
    user_id: int
    reply_to_user_id: int | None
    content_type: int
    content: str
    status: int
    created_at: str
