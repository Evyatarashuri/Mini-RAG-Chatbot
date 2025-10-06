from pymongo import MongoClient
from app.core.config import settings
import gridfs
import os

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

users_collection = db["users"]
documents_collection = db["documents"]


fs = gridfs.GridFS(db)