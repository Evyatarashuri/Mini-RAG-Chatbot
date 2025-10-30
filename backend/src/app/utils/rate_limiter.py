from fastapi import Request, HTTPException
from app.db.redis import redis_client
from typing import Optional

# --- Configuration ---
GENERAL_LIMIT_COUNT = 20  # General API limit (e.g., for template views, general endpoints)
GENERAL_LIMIT_WINDOW = 60 # Time window in seconds (1 minute)

def get_rate_limit_key(request: Request) -> Optional[str]:
    """
    Determines the unique key for rate limiting, prioritizing user ID.
    Assumes authentication middleware has run and set request.state.user.
    """
    # 1. Try to get the authenticated user ID
    user = getattr(request.state, "user", None)
    if user and user.get("_id"):
        return f"ratelimit:user:{user['_id']}"
    
    # 2. Fallback to IP address for unauthenticated requests
    if request.client:
        return f"ratelimit:ip:{request.client.host}"
    
    return None


async def rate_limiter(request: Request, call_next):
    """
    Enforces a general rate limit based on user ID (if authenticated) or IP (if anonymous).
    """
    key = get_rate_limit_key(request)

    # If key cannot be determined (very rare), allow request but log warning
    if not key:
        return await call_next(request)

    count = redis_client.incr(key)
    
    # Set expiration only on the first increment (start of the window)
    if count == 1:
        # Use SETEX or check TTL for better safety, but incr/expire pattern works for simplicity
        redis_client.expire(key, GENERAL_LIMIT_WINDOW)

    if count > GENERAL_LIMIT_COUNT:
        # 429: Too Many Requests
        raise HTTPException(status_code=429, detail="General API rate limit exceeded. Try again in 60 seconds.")

    response = await call_next(request)
    return response
