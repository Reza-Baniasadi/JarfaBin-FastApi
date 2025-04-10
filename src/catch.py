import httpx
import time

client = httpx.AsyncClient(timeout=15.0)

_cache = {}


def set_cache(key: str, value: dict, ttl: int = 30):
    expire_at = time.time() + ttl
    _cache[key] = (value, expire_at)
