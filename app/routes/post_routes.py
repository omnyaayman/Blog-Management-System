from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services import post_service
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return post_service.create_post(db, post, user.id)


@router.get("/", response_model=list[PostResponse])
def get_posts(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    return post_service.get_posts(db, skip, limit)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = post_service.get_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return post_service.update_post(db, post, data)


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = post_service.get_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    post_service.delete_post(db, post)
    return {"message": "Deleted successfully"}



