from sqlalchemy.orm import Session
from app.models.post import Post
from app.core.logger import logger
from app.services import cache_service


def _post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "tags": post.tags or [],
        "author_id": post.author_id,
        "view_count": post.view_count,
        "created_at": str(post.created_at) if post.created_at else None,
        "updated_at": str(post.updated_at) if post.updated_at else None,
    }


def get_posts(db: Session, page: int = 1, limit: int = 10):
    # Cache-Aside: check cache first
    cached = cache_service.get_cached_posts(page, limit)
    if cached is not None:
        return cached

    skip = (page - 1) * limit
    posts = db.query(Post).offset(skip).limit(limit).all()
    posts_data = [_post_to_dict(p) for p in posts]

    cache_service.set_cached_posts(page, limit, posts_data)
    return posts_data


def get_post_by_id(db: Session, post_id: int):
    """Get post from cache or DB. Does NOT increment view_count."""
    cached = cache_service.get_cached_post(post_id)
    if cached is not None:
        return cached

    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        data = _post_to_dict(post)
        cache_service.set_cached_post(post_id, data)
        return data
    return None


def get_post_model(db: Session, post_id: int):
    """Get raw SQLAlchemy model (for mutations)."""
    return db.query(Post).filter(Post.id == post_id).first()


def increment_view(db: Session, post_id: int):
    """Increment view_count directly on DB."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.view_count = (post.view_count or 0) + 1
        db.commit()
        db.refresh(post)
    return post


def create_post(db: Session, data, user_id: int):
    post = Post(
        title=data.title,
        content=data.content,
        tags=data.tags or [],
        author_id=user_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    logger.info(f"Post created id={post.id} by user={user_id}")
    cache_service.invalidate_all_posts()
    return post


def update_post(db: Session, post: Post, data):
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(post, key, value)
    db.commit()
    db.refresh(post)
    logger.info(f"Post updated id={post.id}")
    cache_service.invalidate_post(post.id)
    return post


def delete_post(db: Session, post: Post):
    post_id = post.id
    db.delete(post)
    db.commit()
    logger.info(f"Post deleted id={post_id}")
    cache_service.invalidate_post(post_id)
