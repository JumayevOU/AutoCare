from functools import wraps
from typing import Callable, Optional, Any

def rate_limit(limit: int, key: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for configuring rate limit and key on handler functions.

    Usage:
        @rate_limit(5)                 # limit 5 seconds, key = "module.func"
        async def handler(...): ...

        @rate_limit(2, key="send_msg") # custom key
        def handler(...): ...

    The decorator sets two attributes on the wrapped function:
        - throttling_rate_limit (int)
        - throttling_key (str)

    Your throttling middleware should read these attributes from the handler callable.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        default_key = key or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        async_wrapper.throttling_rate_limit = int(limit)
        async_wrapper.throttling_key = str(default_key)
        try:
            func.throttling_rate_limit = int(limit)
            func.throttling_key = str(default_key)
        except Exception:
            pass

        return async_wrapper  # return wrapper that is always async

    return decorator
