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


def is_rate_limited(ip: str, limit: int = 10, window: int = 60) -> bool:
    key = f"ratelimit:{ip}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, window)
    return count > limit