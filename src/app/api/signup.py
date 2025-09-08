from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.mongo import users_collection
from datetime import datetime, timezone
from app.core.security import hash_password, create_access_token


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/signup", tags=["signup"])


@router.get("/", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def signup(username: str = Form(...), password: str = Form(...), request: Request = None):
    if users_collection.find_one({"username": username}):
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Username already exists"}
        )

    hashed = hash_password(password)
    users_collection.insert_one({
        "username": username,
        "password": hashed,
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    })

    token = create_access_token({"sub": username, "username": username})

    response = RedirectResponse(url="/query", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        path="/"
    )
    return response
