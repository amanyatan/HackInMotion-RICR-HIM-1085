"""Dependency-free in-memory fixed-window rate limiter.

Provides basic abuse protection for the auth endpoints. Suitable for a
single-process deployment; swap for slowapi/Redis if you scale horizontally.
"""

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

from app.core.config import settings


class FixedWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._hits[key]
            bucket[:] = [t for t in bucket if t > cutoff]
            if len(bucket) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please try again in a minute.",
                        }
                    },
                )
            bucket.append(now)
            # keep the dict from growing unboundedly
            if len(self._hits) > 10000:
                self._hits = defaultdict(list)


_limiter = FixedWindowLimiter(max_requests=settings.rate_limit_per_minute)


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    _limiter.check(f"{request.url.path}:{ip}")