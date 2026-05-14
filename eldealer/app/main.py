import time
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.reaction import Reaction
from app.core.logger import logger
from app.core.metrics import metrics_store
from app.core.seed import seed_admin

from app.routes import auth, posts, comments, reactions, admin

# Create all tables
Base.metadata.create_all(bind=engine)

# Seed admin account
db = SessionLocal()
try:
    seed_admin(db)
finally:
    db.close()

app = FastAPI(title="Blog Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register routers ──────────────────────────────────────
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(posts.router_my)
app.include_router(comments.router)
app.include_router(reactions.router)
app.include_router(admin.router)


# ─── Request logging middleware ─────────────────────────────
@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    metrics_store["total_requests"] += 1

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        metrics_store["total_response_time_ms"] += duration_ms

        if response.status_code >= 400:
            metrics_store["total_errors"] += 1

        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.1f}ms)"
        )
        return response
    except Exception as exc:
        metrics_store["total_errors"] += 1
        logger.error(f"Unhandled error: {traceback.format_exc()}")
        raise exc


# ─── Root ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Blog Management System API is running"}


# ─── Metrics endpoint ──────────────────────────────────────
@app.get("/metrics")
def metrics():
    total = metrics_store["total_requests"]
    avg_ms = metrics_store["total_response_time_ms"] / total if total else 0.0

    # Read last 10 ERROR lines from app.log
    recent_errors = []
    try:
        with open("app.log", "r", encoding="utf-8") as f:
            for line in f:
                if "| ERROR" in line:
                    recent_errors.append(line.strip())
            recent_errors = recent_errors[-10:]
    except FileNotFoundError:
        pass

    return {
        "total_requests": metrics_store["total_requests"],
        "total_errors": metrics_store["total_errors"],
        "recent_errors": recent_errors,
        "avg_response_time_ms": round(avg_ms, 2),
        "cache_hits": metrics_store["cache_hits"],
        "cache_misses": metrics_store["cache_misses"],
    }