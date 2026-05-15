from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services import comment_service
from app.services.permissions import check_owner
from app.models.post import Post
from app.models.comment import Comment

router = APIRouter(tags=["Comments"])


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def add_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return comment_service.create_comment(db, data.content, user.id, post_id)


@router.post(
    "/posts/{post_id}/comments/{comment_id}/reply",
    response_model=CommentResponse,
)
def reply_to_comment(
    post_id: int,
    comment_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    parent = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    return comment_service.create_comment(db, data.content, user.id, post_id, parent_id=comment_id)


@router.get("/posts/{post_id}/comments")
def list_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = comment_service.get_comments_for_post(db, post_id)
    return [
        {
            "id": c.id,
            "content": c.content,
            "user_id": c.user_id,
            "post_id": c.post_id,
            "parent_id": c.parent_id,
            "created_at": str(c.created_at) if c.created_at else None,
        }
        for c in comments
    ]


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    comment = comment_service.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    check_owner(comment.user_id, user)
    return comment_service.update_comment(db, comment, data.content)


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    comment = comment_service.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    check_owner(comment.user_id, user)
    comment_service.delete_comment(db, comment)
    return {"message": "Comment deleted successfully"}
