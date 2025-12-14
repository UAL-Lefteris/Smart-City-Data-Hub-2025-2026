import redis
import json
from typing import Optional, Any, Callable
from functools import wraps
from src.database.config import Config


class CacheManager:
    def __init__(self):
        self.client = redis.from_url(
            Config.CACHE_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self.default_ttl = Config.CACHE_TTL

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            return self.client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        try:
            keys = self.client.keys(pattern)
            return self.client.delete(*keys) if keys else 0
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return 0


cache = CacheManager()


def cached(key_prefix: str, ttl: Optional[int] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args[1:])}"

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args[1:])}"

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        import inspect
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator