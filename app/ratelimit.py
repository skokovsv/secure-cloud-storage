import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.max_requests:
                retry_after = int(self.window - (now - hits[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)


_login_limiter = RateLimiter(max_requests=5, window_seconds=60)
_register_limiter = RateLimiter(max_requests=10, window_seconds=3600)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def limit_login(request: Request) -> None:
    _login_limiter.check(_client_ip(request))


def limit_register(request: Request) -> None:
    _register_limiter.check(_client_ip(request))
