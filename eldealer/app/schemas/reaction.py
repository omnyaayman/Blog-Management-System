from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ReactionType(str, Enum):
    like = "like"
    love = "love"
    haha = "haha"
    sad = "sad"
    angry = "angry"


class ReactionCreate(BaseModel):
    type: ReactionType


class ReactionResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    type: str

    class Config:
        from_attributes = True


class ReactionToggleResponse(BaseModel):
    action: str  # "added", "changed", "removed"
    reaction: Optional[ReactionResponse] = None
