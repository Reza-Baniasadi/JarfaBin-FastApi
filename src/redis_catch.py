import redis
import time
import logging
from config import settings

redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

logger = logging.getLogger("crypto_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def set_cache(key: str, value: str, ttl: int = 30):
    redis_client.setex(key, ttl, value)


def get_cache(key: str):
    return redis_client.get(key)


def is_rate_limited(ip: str, limit: int = 20, window: int = 60) -> bool:
    key = f"ratelimit:{ip}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, window)
    return count > limit


@app.middleware("http")
async def log_and_limit(request: Request, call_next):
    ip = request.client.host
    if is_rate_limited(ip):
        return HTTPException(status_code=429, detail="Too many requests")
    logger.info(f"{ip} - {request.method} {request.url}")
    response = await call_next(request)
    return response