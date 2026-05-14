from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class PostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[List[str]] = []
    author_id: int
    view_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostStatsResponse(BaseModel):
    post_id: int
    title: str
    view_count: int
    comment_count: int
    reactions: Dict[str, int] = {}