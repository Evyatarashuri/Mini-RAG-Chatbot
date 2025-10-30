from app.core.logging import logger
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
    """
    Decode a JWT token and return the payload.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Successfully decoded payload: {payload}")
        return payload
    except JWTError as e:
        logger.debug(f"JWTError: {str(e)}")
        return None
    except Exception as e:
        logger.debug(f"Unexpected error in decode: {str(e)}")
        return None
