import json
from app.core.redis_client import redis_client
from app.core.logger import logger
from app.core.metrics import metrics_store

POSTS_LIST_TTL = 60   # seconds
POST_DETAIL_TTL = 120  # seconds


# ─── Read helpers ───────────────────────────────────────────

def get_cached_posts(page: int, limit: int):
    if not redis_client:
        return None
    key = f"posts:page:{page}:limit:{limit}"
    try:
        data = redis_client.get(key)
        if data:
            logger.debug(f"Cache HIT for key {key}")
            metrics_store["cache_hits"] += 1
            return json.loads(data)
        logger.debug(f"Cache MISS for key {key}, fetching from DB")
        metrics_store["cache_misses"] += 1
        return None
    except Exception as e:
        logger.warning(f"Redis read error: {e}")
        return None


def set_cached_posts(page: int, limit: int, data):
    if not redis_client:
        return
    key = f"posts:page:{page}:limit:{limit}"
    try:
        redis_client.setex(key, POSTS_LIST_TTL, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis write error: {e}")


def get_cached_post(post_id: int):
    if not redis_client:
        return None
    key = f"post:{post_id}"
    try:
        data = redis_client.get(key)
        if data:
            logger.debug(f"Cache HIT for key {key}")
            metrics_store["cache_hits"] += 1
            return json.loads(data)
        logger.debug(f"Cache MISS for key {key}, fetching from DB")
        metrics_store["cache_misses"] += 1
        return None
    except Exception as e:
        logger.warning(f"Redis read error: {e}")
        return None


def set_cached_post(post_id: int, data):
    if not redis_client:
        return
    key = f"post:{post_id}"
    try:
        redis_client.setex(key, POST_DETAIL_TTL, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis write error: {e}")


# ─── Invalidation ──────────────────────────────────────────

def invalidate_post(post_id: int):
    """Delete single-post cache and all list caches."""
    if not redis_client:
        return
    try:
        redis_client.delete(f"post:{post_id}")
        _delete_pattern("posts:page:*")
        logger.debug(f"Cache invalidated for post:{post_id} + list pages")
    except Exception as e:
        logger.warning(f"Redis invalidation error: {e}")


def invalidate_all_posts():
    """Delete all list caches."""
    if not redis_client:
        return
    try:
        _delete_pattern("posts:page:*")
        logger.debug("Cache invalidated for all post list pages")
    except Exception as e:
        logger.warning(f"Redis invalidation error: {e}")


def _delete_pattern(pattern: str):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
