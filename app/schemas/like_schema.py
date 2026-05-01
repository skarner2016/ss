from pydantic import BaseModel


class LikeDoRequest(BaseModel):
    target_type: int
    target_id: int


class LikeCancelRequest(BaseModel):
    target_type: int
    target_id: int
