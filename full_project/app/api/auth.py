from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_refresh_token, verify_password, create_access_token, get_current_user
)
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse, ChangePassword
from app.services import refresh_token_service, user_service
from app.core.helpers import register_failed_login_attempt, check_if_user_blocked, reset_failed_attempts
from jose import JWTError, jwt
from app.core.config import settings
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new account.
    - Email must be unique
    - Password is hashed before storing — never stored as plain text
    """
    existing = user_service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return user_service.create_user(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT token",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email + password.
    Returns a JWT access token — send this as:
    Authorization: Bearer <token>
    in all protected routes.
    """
    user = user_service.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    check_if_user_blocked(user)

    if not verify_password(data.password, user.hashed_password):
        register_failed_login_attempt(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    reset_failed_attempts(user)
    db.commit()
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    token = create_access_token(data={"sub": user.email})
    refresh_token, token_id, expires_at = (
    create_refresh_token(
            {"sub": user.email}
        )
    )

    refresh_token_service.create_token(
        db=db,
        user_id=user.id,
        token_id=token_id,
        expires_at=expires_at
    )
    return {"access_token": token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user",
)
def get_me(current_user=Depends(get_current_user)):
    """Returns the profile of whoever is logged in (based on their JWT token)."""
    return current_user


@router.patch(
    "/change-password",
    summary="Change your password",
)
def change_password(
    data: ChangePassword,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    from app.core.security import hash_password
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/refresh", summary="Refresh access token")
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        jti = payload.get("jti")

        if not jti:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    stored_token = refresh_token_service.get_by_token_id(
        db,
        jti
    )

    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found"
        )

    if stored_token.is_revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked"
        )

    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    user = user_service.get_user_by_id(
        db,
        stored_token.user_id
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # Revoke old refresh token (rotation)
    refresh_token_service.revoke_token(
        db,
        jti
    )

    # Generate new tokens
    new_access_token = create_access_token(
        {"sub": user.email}
    )

    new_refresh_token, new_jti, expires_at = (
        create_refresh_token(
            {"sub": user.email}
        )
    )

    # Save new refresh token
    refresh_token_service.create_token(
        db=db,
        user_id=user.id,
        token_id=new_jti,
        expires_at=expires_at
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        jti = payload.get("jti")

        if not jti:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    token_record = refresh_token_service.revoke_token(
        db,
        jti
    )

    if not token_record:
        raise HTTPException(
            status_code=404,
            detail="Refresh token not found"
        )

    return {
        "message": "Logged out successfully"
    }