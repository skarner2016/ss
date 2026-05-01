from pydantic import BaseModel, Field


class FavoriteDoRequest(BaseModel):
    post_id: int


class FavoriteCancelRequest(BaseModel):
    post_id: int


class FavoriteListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class FavoriteInfo(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: str
