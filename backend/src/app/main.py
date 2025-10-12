from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.api import api_router
from app.core.middleware import setup_middlewares
from app.api.routes import query_api, documents_api, login_api

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title=settings.PROJECT_NAME)

# Templates & static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Middlewares (CORS + JWT + Rate Limiter)
setup_middlewares(app)

# Routers
app.include_router(api_router)
app.include_router(query_api.router)
app.include_router(documents_api.router)
app.include_router(login_api.router)


# To create - app.on_event ("startup")(create_start_app_handler(app))