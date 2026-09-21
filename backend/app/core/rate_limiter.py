from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request

from app.core.errors import RateLimitExceededError


class InMemoryRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._records: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        current_time = time.time()
        threshold = current_time - window_seconds

        with self._lock:
            # Filter out timestamps outside current sliding window
            valid_timestamps = [t for t in self._records[key] if t > threshold]
            if len(valid_timestamps) >= max_requests:
                self._records[key] = valid_timestamps
                return False

            valid_timestamps.append(current_time)
            self._records[key] = valid_timestamps
            return True

    def reset(self) -> None:
        with self._lock:
            self._records.clear()


limiter = InMemoryRateLimiter()


def rate_limit(max_requests: int = 5, window_seconds: int = 60) -> Callable:
    """FastAPI dependency for rate limiting by client IP."""

    async def _dependency(request: Request) -> None:
        client_ip = (
            request.headers.get("x-forwarded-for")
            or (request.client.host if request.client else "unknown")
        )
        # In case of multiple forwarded IPs, take the first one
        client_ip = client_ip.split(",")[0].strip()
        key = f"{request.url.path}:{client_ip}"

        if not limiter.is_allowed(key, max_requests=max_requests, window_seconds=window_seconds):
            raise RateLimitExceededError("RATE_LIMIT_EXCEEDED")

    return _dependency
