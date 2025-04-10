import httpx
import time

client = httpx.AsyncClient(timeout=15.0)

_cache = {}


def set_cache(key: str, value: dict, ttl: int = 30):
    expire_at = time.time() + ttl
    _cache[key] = (value, expire_at)


def get_cache(key: str):
    data = _cache.get(key)
    if not data:
        return None
    value, expire_at = data
    if time.time() > expire_at:
        _cache.pop(key, None)
        return None
    return value