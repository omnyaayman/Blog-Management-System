import redis
from app.config import REDIS_HOST, REDIS_PORT
from app.core.logger import logger

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )
    redis_client.ping()
    logger.info(f"Redis connected at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.warning(f"Redis unavailable: {e}. Caching disabled.")
    redis_client = None