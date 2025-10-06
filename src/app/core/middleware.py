from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.core.security import decode_access_token
from app.db.mongo import users_collection
from bson import ObjectId

PROTECTED_PATHS = ("/documents", "/query", "/upload")

def setup_middlewares(app):
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """
        JWT middleware that supports both Header and Cookie authentication.
        Redirects unauthenticated users to /login for protected pages.
        """
        path = request.url.path

        # Check if the requested path requires authentication
        if path.startswith(PROTECTED_PATHS):
            token = None

            # Try to get token from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            # Try to get token from Cookie
            if not token:
                cookie_token = request.cookies.get("access_token")
                if cookie_token and cookie_token.startswith("Bearer "):
                    token = cookie_token.split(" ")[1]

            # No token found
            if not token:
                # If the client expects HTML, redirect to login page
                if "text/html" in request.headers.get("accept", ""):
                    return RedirectResponse(url="/login", status_code=303)
                # Otherwise, return JSON error (for API requests)
                return JSONResponse(status_code=401, content={"error": "Missing token"})

            # Validate the token and extract user info
            try:
                payload = decode_access_token(token)
                if not payload:
                    if "text/html" in request.headers.get("accept", ""):
                        return RedirectResponse(url="/login", status_code=303)
                    return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

                user_id = payload.get("sub")
                if not user_id or not ObjectId.is_valid(user_id):
                    return JSONResponse(status_code=401, content={"error": "Invalid user ID in token"})

                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if not user:
                    return JSONResponse(status_code=401, content={"error": "User not found"})

                # Attach user object to request state
                request.state.user = user

            except Exception as e:
                # Redirect HTML clients, return JSON for API calls
                if "text/html" in request.headers.get("accept", ""):
                    return RedirectResponse(url="/login", status_code=303)
                return JSONResponse(status_code=401, content={"error": str(e)})

        # Continue with the request
        response = await call_next(request)
        return response
