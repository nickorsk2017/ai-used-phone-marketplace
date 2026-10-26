"""Rate limits of the modules, per client IP: docs/INFRA.md#application."""

import math
import time
from collections import deque
from collections.abc import Callable
from typing import ClassVar

from fastapi import HTTPException, Request, status

UNKNOWN_CLIENT = "unknown"


class RateLimit:
    """Sliding window limit, a FastAPI dependency. Counters live in the memory of the process."""

    _instances: ClassVar[list["RateLimit"]] = []

    def __init__(self, limit: int, window_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._last_sweep = clock()
        RateLimit._instances.append(self)

    async def __call__(self, request: Request) -> None:
        now = self._clock()
        self._sweep(now)
        hits = self._hits.setdefault(request.client.host if request.client else UNKNOWN_CLIENT, deque())
        while hits and hits[0] <= now - self.window_seconds:
            hits.popleft()
        if len(hits) >= self.limit:
            retry_after = max(1, math.ceil(hits[0] + self.window_seconds - now))
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests", headers={"Retry-After": str(retry_after)}
            )
        hits.append(now)

    def _sweep(self, now: float) -> None:
        """Drops the counters of clients without requests in the last window, so memory does not grow."""
        if now - self._last_sweep < self.window_seconds:
            return
        self._last_sweep = now
        expired = [key for key, hits in self._hits.items() if not hits or hits[-1] <= now - self.window_seconds]
        for key in expired:
            del self._hits[key]

    def reset(self) -> None:
        self._hits.clear()

    @classmethod
    def reset_all(cls) -> None:
        for instance in cls._instances:
            instance.reset()


users_rate_limit = RateLimit(limit=5, window_seconds=10)
# One counter per endpoint of `modules/phones`.
phones_description_rate_limit = RateLimit(limit=1, window_seconds=10)
phones_create_rate_limit = RateLimit(limit=1, window_seconds=10)
my_listings_rate_limit = RateLimit(limit=5, window_seconds=10)
# `POST /api/search`: protection against cost attacks on OpenAI.
search_rate_limit = RateLimit(limit=3, window_seconds=10)
