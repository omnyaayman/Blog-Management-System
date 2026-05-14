from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.reaction import ReactionCreate, ReactionToggleResponse, ReactionResponse
from app.models.reaction import Reaction
from app.models.post import Post
from app.core.logger import logger

router = APIRouter(tags=["Reactions"])


@router.post("/posts/{post_id}/react", response_model=ReactionToggleResponse)
def toggle_reaction(
    post_id: int,
    data: ReactionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(Reaction)
        .filter(Reaction.user_id == user.id, Reaction.post_id == post_id)
        .first()
    )

    if existing:
        if existing.type == data.type.value:
            # Same type → toggle off (remove)
            db.delete(existing)
            db.commit()
            logger.info(f"Reaction removed: user={user.id} post={post_id} type={data.type.value}")
            return {"action": "removed", "reaction": None}
        else:
            # Different type → update
            existing.type = data.type.value
            db.commit()
            db.refresh(existing)
            logger.info(f"Reaction changed: user={user.id} post={post_id} type={data.type.value}")
            return {
                "action": "changed",
                "reaction": ReactionResponse.model_validate(existing),
            }
    else:
        # New reaction
        reaction = Reaction(user_id=user.id, post_id=post_id, type=data.type.value)
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        logger.info(f"Reaction added: user={user.id} post={post_id} type={data.type.value}")
        return {
            "action": "added",
            "reaction": ReactionResponse.model_validate(reaction),
        }
