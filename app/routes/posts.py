from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostStatsResponse
from app.services import post_service
from app.services.permissions import check_owner
from app.dependencies import get_db, get_current_user, require_role
from app.models.comment import Comment
from app.models.reaction import Reaction
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin", "author"])),
):
    post = post_service.create_post(db, data, user.id)
    return post


@router.get("/")
def list_posts(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    return post_service.get_posts(db, page, limit)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    # Increment view count directly on DB (not cached)
    post_service.increment_view(db, post_id)

    data = post_service.get_post_by_id(db, post_id)
    if not data:
        raise HTTPException(status_code=404, detail="Post not found")

    # Refresh view_count from DB since cache may have stale value
    model = post_service.get_post_model(db, post_id)
    if model and isinstance(data, dict):
        data["view_count"] = model.view_count
    return data


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = post_service.get_post_model(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    check_owner(post.author_id, user)
    return post_service.update_post(db, post, data)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = post_service.get_post_model(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    check_owner(post.author_id, user)
    post_service.delete_post(db, post)
    return {"message": "Post deleted successfully"}


@router.get("/{post_id}/stats", response_model=PostStatsResponse)
def post_stats(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post_model(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_count = db.query(sql_func.count(Comment.id)).filter(Comment.post_id == post_id).scalar()
    reactions = (
        db.query(Reaction.type, sql_func.count(Reaction.id))
        .filter(Reaction.post_id == post_id)
        .group_by(Reaction.type)
        .all()
    )
    reactions_dict = {r_type: count for r_type, count in reactions}

    return {
        "post_id": post.id,
        "title": post.title,
        "view_count": post.view_count,
        "comment_count": comment_count,
        "reactions": reactions_dict,
    }


router_my = APIRouter(tags=["My Posts"])


@router_my.get("/my/posts")
def my_posts(
    db: Session = Depends(get_db),
    user=Depends(require_role(["author", "admin"])),
):
    posts = db.query(Post).filter(Post.author_id == user.id).all()
    result = []
    for p in posts:
        cc = db.query(sql_func.count(Comment.id)).filter(Comment.post_id == p.id).scalar()
        result.append({
            "id": p.id,
            "title": p.title,
            "view_count": p.view_count,
            "comment_count": cc,
            "created_at": str(p.created_at) if p.created_at else None,
        })
    return result
