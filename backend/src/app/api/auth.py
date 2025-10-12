from fastapi import Cookie, HTTPException, Depends
from bson import ObjectId
from app.core.security import decode_access_token
from app.db.mongo import users_collection

def get_current_user_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = access_token.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload["sub"]
    user = users_collection.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
