from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    post_id: int
    content: str = Field(min_length=1)


class CommentDeleteRequest(BaseModel):
    comment_id: int


class CommentListRequest(BaseModel):
    post_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CommentInfo(BaseModel):
    id: int
    post_id: int
    user_id: int
    content_type: int
    content: str
    reply_count: int
    status: int
    created_at: str
