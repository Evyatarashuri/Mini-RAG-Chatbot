from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.rate_limiter import rate_limiter
from app.core.security import decode_access_token
from app.db.mongo import users_collection
from bson import ObjectId
from fastapi.responses import JSONResponse


def setup_middlewares(app: FastAPI):
    """
    Centralized middleware setup for FastAPI app.
    Includes: CORS, JWT authentication, and rate limiting.
    """

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # frontend origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate Limiter
    app.middleware("http")(rate_limiter)

    # JWT Validation Middleware
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
                print(f"[DEBUG] Cookie token: {cookie_token}")  # Debug log
                if cookie_token:
                    # Support both "Bearer TOKEN" and just "TOKEN"
                    if cookie_token.startswith("Bearer "):
                        token = cookie_token.split(" ")[1]
                    else:
                        token = cookie_token

            if not token:
                print(f"[DEBUG] Missing token for path: {request.url.path}")  # Debug log
                return JSONResponse(status_code=401, content={"error": "Missing token"})

            try:
                payload = decode_access_token(token)
                print(f"[DEBUG] Decoded payload: {payload}")  # Debug log
                if not payload:
                    print("[DEBUG] Invalid or expired token")  # Debug log
                    return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

                user_id = payload.get("sub")
                if not user_id or not ObjectId.is_valid(user_id):
                    print(f"[DEBUG] Invalid user ID: {user_id}")  # Debug log
                    return JSONResponse(status_code=401, content={"error": "Invalid user ID in token"})

                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if not user:
                    print(f"[DEBUG] User not found: {user_id}")  # Debug log
                    return JSONResponse(status_code=401, content={"error": "User not found"})

                request.state.user = user

            except Exception as e:
                print(f"[DEBUG] Exception in auth middleware: {str(e)}")  # Debug log
                return JSONResponse(status_code=401, content={"error": str(e)})

        response = await call_next(request)
        return response
