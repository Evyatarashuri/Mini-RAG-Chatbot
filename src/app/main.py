from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.api import api_router
from app.core.middleware import setup_middlewares
from app.utils.rate_limiter import rate_limiter

app = FastAPI(title=settings.PROJECT_NAME)

templates = Jinja2Templates(directory="src/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# middlewares
setup_middlewares(app)
app.middleware("http")(rate_limiter)

# routers
app.include_router(api_router)
