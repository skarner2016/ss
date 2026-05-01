from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(min_length=1)


class PostUpdateRequest(BaseModel):
    post_id: int
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None


class PostDeleteRequest(BaseModel):
    post_id: int


class PostListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


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
