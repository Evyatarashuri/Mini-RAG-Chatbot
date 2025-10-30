from app.core.logging import logger
from fastapi import Cookie, HTTPException, Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_class=HTMLResponse)
async def get_profile(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
