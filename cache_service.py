"""
Сервис кэширования (аналог IDistributedCache + Redis)
In-memory кэш с TTL
"""
import time
import threading
from typing import Any, Optional
import json

class CacheService:
    def __init__(self, default_ttl_seconds: int = 60):
        self._cache = {}
        self._expiry = {}
        self._default_ttl = default_ttl_seconds
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        with self._lock:
            self._cache[key] = value
            ttl = ttl_seconds or self._default_ttl
            self._expiry[key] = time.time() + ttl
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._expiry.clear()

# Глобальный экземпляр кэша
cache = CacheService(default_ttl_seconds=30)

def cached(ttl_seconds: int = 30):
    """Декоратор для кэширования результатов функции"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator
