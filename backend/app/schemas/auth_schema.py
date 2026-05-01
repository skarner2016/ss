from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UpdateMeRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=500)


class UserInfo(BaseModel):
    id: int
    email: str
    nickname: str | None
    avatar_url: str | None
    bio: str | None
    status: int
    created_at: str


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
