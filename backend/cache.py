from __future__ import annotations

import json
from typing import Any

from configs.settings import CACHE_TTL_SECONDS, REDIS_URL

try:
    import redis
except ImportError:  # pragma: no cover - optional until dependencies are installed
    redis = None


class RedisCache:
    def __init__(self, url: str = REDIS_URL, ttl_seconds: int = CACHE_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds
        self.client = None
        if redis is not None:
            try:
                self.client = redis.Redis.from_url(url, decode_responses=True)
                self.client.ping()
            except Exception:
                self.client = None

    @property
    def available(self) -> bool:
        return self.client is not None

    def get_json(self, key: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        value = self.client.get(key)
        if not value:
            return None
        return json.loads(value)

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        if not self.client:
            return
        self.client.setex(key, ttl_seconds or self.ttl_seconds, json.dumps(value, default=str))


cache = RedisCache()
