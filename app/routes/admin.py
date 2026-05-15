from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from app.dependencies import get_db, require_role
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.reaction import Reaction
from app.schemas.user import RoleUpdate
from app.services import post_service
from app.schemas.post import PostUpdate
from app.core.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(require_role(["admin"]))):
    users = db.query(User).all()
    result = []
    for u in users:
        pc = db.query(sql_func.count(Post.id)).filter(Post.author_id == u.id).scalar()
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "post_count": pc,
            "created_at": str(u.created_at) if u.created_at else None,
        })
    return result


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_role(["admin"]))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pc = db.query(sql_func.count(Post.id)).filter(Post.author_id == user.id).scalar()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "post_count": pc,
        "created_at": str(user.created_at) if user.created_at else None,
    }


@router.put("/users/{user_id}/role")
def change_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role(["admin"])),
):
    if data.role not in ("author", "reader"):
        raise HTTPException(status_code=400, detail="Role must be 'author' or 'reader'")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old_role = user.role
    user.role = data.role
    db.commit()
    logger.info(f"Admin changed user {user_id} role from {old_role} to {data.role}")
    return {"message": f"Role updated to {data.role}"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_role(["admin"])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Delete cascades handle posts/comments/reactions via FK
    db.delete(user)
    db.commit()
    logger.info(f"Admin deleted user {user_id}")
    return {"message": "User and all their content deleted"}


@router.delete("/posts/{post_id}")
def admin_delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_role(["admin"])),
):
    post = post_service.get_post_model(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_service.delete_post(db, post)
    return {"message": "Post deleted by admin"}


@router.put("/posts/{post_id}")
def admin_update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role(["admin"])),
):
    post = post_service.get_post_model(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    updated = post_service.update_post(db, post, data)
    return {
        "id": updated.id,
        "title": updated.title,
        "content": updated.content,
        "tags": updated.tags,
        "author_id": updated.author_id,
        "view_count": updated.view_count,
    }


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), admin=Depends(require_role(["admin"]))):
    total_users = db.query(sql_func.count(User.id)).scalar()
    total_posts = db.query(sql_func.count(Post.id)).scalar()
    total_comments = db.query(sql_func.count(Comment.id)).scalar()
    total_reactions = db.query(sql_func.count(Reaction.id)).scalar()
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_reactions": total_reactions,
    }
