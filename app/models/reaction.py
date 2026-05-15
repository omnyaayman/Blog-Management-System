from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # like, love, haha, sad, angry

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_reaction"),
    )
