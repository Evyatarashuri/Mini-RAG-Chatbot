from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.security import decode_access_token
from app.db.mongo import users_collection
from bson import ObjectId


def setup_middlewares(app):
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """JWT middleware that supports both Header and Cookie"""
        if request.url.path.startswith(("/documents", "/query")):
            token = None

            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                cookie_token = request.cookies.get("access_token")
                if cookie_token and cookie_token.startswith("Bearer "):
                    token = cookie_token.split(" ")[1]

            if not token:
                return JSONResponse(status_code=401, content={"error": "Missing token"})

            try:
                payload = decode_access_token(token)
                if not payload:
                    return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

                user_id = payload.get("sub")
                if not user_id or not ObjectId.is_valid(user_id):
                    return JSONResponse(status_code=401, content={"error": "Invalid user ID in token"})

                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if not user:
                    return JSONResponse(status_code=401, content={"error": "User not found"})

                request.state.user = user

            except Exception as e:
                return JSONResponse(status_code=401, content={"error": str(e)})

        response = await call_next(request)
        return response
