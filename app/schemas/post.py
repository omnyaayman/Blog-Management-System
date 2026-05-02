from pydantic import BaseModel
from typing import Optional

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int

    class Config:
        orm_mode = True


        