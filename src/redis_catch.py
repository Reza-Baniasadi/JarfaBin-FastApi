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