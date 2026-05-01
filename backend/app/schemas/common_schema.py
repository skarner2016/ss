from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = 0
    message: str = "OK"
    data: dict | list | None = None


class PageRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PageData(BaseModel):
    items: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
