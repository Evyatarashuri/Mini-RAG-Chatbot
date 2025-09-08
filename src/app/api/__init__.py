from fastapi import APIRouter
from app.api import login, signup, documents, query

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(signup.router)
api_router.include_router(documents.router)
api_router.include_router(query.router)
