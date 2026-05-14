from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth_service import hash_password
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME
from app.core.logger import logger


def seed_admin(db: Session):
    """Seed the admin account from .env credentials. Skip if already exists."""
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        logger.info("Admin account already exists, skipping seed")
        return
    admin = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=hash_password(ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)
    db.commit()
    logger.info(f"Admin account seeded: {ADMIN_EMAIL}")
