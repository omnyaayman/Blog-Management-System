from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.core.logger import logger


def create_comment(db: Session, content: str, user_id: int, post_id: int, parent_id: int = None):
    comment = Comment(
        content=content,
        user_id=user_id,
        post_id=post_id,
        parent_id=parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    logger.info(f"Comment created id={comment.id} on post={post_id} by user={user_id}")
    return comment


def get_comments_for_post(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).all()


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def update_comment(db: Session, comment: Comment, content: str):
    comment.content = content
    db.commit()
    db.refresh(comment)
    logger.info(f"Comment updated id={comment.id}")
    return comment


def delete_comment(db: Session, comment: Comment):
    comment_id = comment.id
    db.delete(comment)
    db.commit()
    logger.info(f"Comment deleted id={comment_id}")
