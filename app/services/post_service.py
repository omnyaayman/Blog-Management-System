from sqlalchemy.orm import Session
from app.models.post import Post


# 🔹 GET ALL (مع pagination)
def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()



def create_post(db: Session, data, user_id: int):
    post = Post(**data.dict(), author_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post



def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


#  UPDATE
def update_post(db: Session, post_id: int, data):
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        return None

    for key, value in data.dict().items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post



def delete_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        return None

    db.delete(post)
    db.commit()
    return post






