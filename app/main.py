# app/main.py

from fastapi import FastAPI

from app.database import engine, Base
from app.models.user import User
from app.routes import auth

# إنشاء الجداول تلقائيًا في قاعدة البيانات
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog Management System"
)

# ربط جميع routes
app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "message": "API is running successfully"
    }



from app.routes import post_routes

app.include_router(post_routes.router, prefix="/posts", tags=["Posts"])


