from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from app.db.mongo import users_collection
from app.core.security import verify_password, create_access_token
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/login", tags=["login"])


@router.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    token = create_access_token({"sub": str(user["_id"]), "username": user["username"]})

    response = RedirectResponse(url="/profile", status_code=303)

    # Save the token in the browser cookies
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        path="/"
    )
    return response
