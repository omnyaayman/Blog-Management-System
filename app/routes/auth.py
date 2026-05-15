from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.core.logger import logger

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role="reader",  # Always reader on registration
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User registered: {new_user.email} as {new_user.role}")
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        logger.warning(f"Failed login attempt for {user.email}")
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user.password):
        logger.warning(f"Failed login attempt for {user.email}")
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(db_user.id)
    logger.info(f"User {db_user.email} logged in with role {db_user.role}")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(user=Depends(get_current_user)):
    return user