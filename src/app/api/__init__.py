from fastapi import APIRouter
from app.api import login, signup, query, logout
from . import upload

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(signup.router)
api_router.include_router(upload.router)
api_router.include_router(query.router)
api_router.include_router(logout.router)
