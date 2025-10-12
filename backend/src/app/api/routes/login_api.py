from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from app.db.mongo import users_collection
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.logging import logger

router = APIRouter(prefix="/api/login", tags=["api-login"])

@router.post("/")
async def login_api(username: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        logger.warning(f"Failed login attempt for username: {username}")
        return JSONResponse(status_code=401, content={"error": "Invalid username or password"})

    logger.info(f"User {username} logged in successfully")

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "username": user["username"]},
        expires_delta=60,
    )

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="none",
        secure=False,       # Set to True in production with HTTPS
        path="/",
    )
    return response
