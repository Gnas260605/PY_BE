from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, Hashable

from core.config import config


class TTLCache:
    def __init__(self, ttl_seconds: int | None = None, max_size: int = 128) -> None:
        self.ttl_seconds = ttl_seconds or config.CACHE_TTL_SECONDS
        self.max_size = max_size
        self._items: OrderedDict[Hashable, tuple[Any, float]] = OrderedDict()

    def get(self, key: Hashable) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None

        value, stored_at = item
        if time.time() - stored_at > self.ttl_seconds:
            self._items.pop(key, None)
            return None

        self._items.move_to_end(key)
        return value

    def set(self, key: Hashable, value: Any) -> None:
        self._items[key] = (value, time.time())
        self._items.move_to_end(key)
        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()


service_cache = TTLCache()


async def cached(key: Hashable, loader: Callable[[], Any], *, refresh: bool = False) -> Any:
    if not refresh:
        cached_value = service_cache.get(key)
        if cached_value is not None:
            return cached_value

    value = await loader()
    service_cache.set(key, value)
    return value
