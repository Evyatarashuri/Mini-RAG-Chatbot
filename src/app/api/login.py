from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from app.db.mongo import users_collection
from app.core.security import verify_password, create_access_token


templates = Jinja2Templates(directory="src/templates")

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

    response = RedirectResponse(url="/query", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        path="/"
    )
    return response
