from fastapi import Request, HTTPException
from app.db.redis import redis_client


async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    key = f"ratelimit:{ip}"

    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)  # reset after 60s

    if count > 20:  # 20 requests/minute
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response
