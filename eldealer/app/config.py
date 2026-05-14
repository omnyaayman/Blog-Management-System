import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@blog.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
