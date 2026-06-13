from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ─── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    try:
        return pwd_context.hash(plain_password)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Password must be between 6 and 72 characters long",
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token with an expiry time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the subject (user email)."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None


# ─── Current user dependency ───────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency — extracts and validates the JWT from the
    Authorization header, then returns the logged-in User object.
    Use this in any route that requires authentication.
    """
    from app.services.user_service import get_user_by_email

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if not email:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_admin(current_user=Depends(get_current_user)):
    """Dependency — only allows users with role='admin'."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

# ─── Refresh token dependency ───────────────────────────────────────────────────

def create_refresh_token(data: dict):

    token_id = str(uuid.uuid4())

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=7)

    payload.update({
        "jti": token_id,
        "type": "refresh",
        "exp": expire
    })

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return token, token_id, expire