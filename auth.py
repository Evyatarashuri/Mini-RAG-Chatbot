from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets
import os
from dotenv import load_dotenv


load_dotenv()


router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Load environment variables
USER = os.getenv("USER")
PASS = os.getenv("PASS")

# Check if they are set
if not USER or not PASS:
    raise RuntimeError("Missing USER or PASS environment variables")

# In-memory session store
sessions = {}

@router.get("/login")
def login_form(request: Request):
    """Render the login form."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """Handle user login and create a session."""
    if username != USER or not secrets.compare_digest(password, PASS):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = f"token-{username}"
    sessions[token] = username
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session_token", value=token)
    return response

def get_current_user(request: Request):
    """Get the current authenticated user from the request."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return sessions[token]
