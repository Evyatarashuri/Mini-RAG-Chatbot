from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.api import api_router
from app.core.middleware import setup_middlewares
from app.utils.rate_limiter import rate_limiter

# BASE_DIR points to /code
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.PROJECT_NAME)

# Templates and static
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Middlewares
setup_middlewares(app)
app.middleware("http")(rate_limiter)

# Routers
app.include_router(api_router)
