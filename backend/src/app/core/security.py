import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(data: dict, expires_delta: int | timedelta = 60):
    """
    Create a JWT token with an expiration time.
    - expires_delta: can be int (minutes) or timedelta.
    """
    to_encode = data.copy()

    if isinstance(expires_delta, int):
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + expires_delta

    # Use timestamp instead of datetime object
    to_encode.update({"exp": int(expire.timestamp())})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str):
    try:
        print(f"[DEBUG] Decoding token: {token[:50]}...")  # Debug log
        print(f"[DEBUG] Using SECRET_KEY: {settings.SECRET_KEY[:10]}...")  # Debug log
        print(f"[DEBUG] Using ALGORITHM: {settings.ALGORITHM}")  # Debug log
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"[DEBUG] Successfully decoded payload: {payload}")  # Debug log
        return payload
    except JWTError as e:
        print(f"[DEBUG] JWTError: {str(e)}")  # Debug log
        return None
    except Exception as e:
        print(f"[DEBUG] Unexpected error in decode: {str(e)}")  # Debug log
        return None
