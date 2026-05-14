from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, func
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[])
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())