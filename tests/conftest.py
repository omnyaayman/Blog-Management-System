import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models.user import User
from app.services.auth_service import hash_password

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_admin(db):
    existing = db.query(User).filter(User.email == "admin@blog.com").first()
    if not existing:
        admin = User(
            username="admin",
            email="admin@blog.com",
            password=hash_password("admin123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)


def _get_token(client, email, password):
    res = client.post("/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, db, username, email, password, role="reader"):
    client.post("/register", json={
        "username": username, "email": email, "password": password
    })
    # Manually promote in DB for testing purposes
    if role != "reader":
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = role
            db.commit()
            
    return _get_token(client, email, password)
