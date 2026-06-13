from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Get all users (admin only)",
)
def list_users(
    skip: int = Query(0, ge=0, description="How many records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),        # only admins can list all users
):
    """
    Returns a paginated list of all users.
    Requires admin role.
    Query params: ?skip=0&limit=10
    """
    return user_service.get_all_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID (admin only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update your own profile",
)
def update_me(
    data: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update your own name or email.
    Only the logged-in user can update their own profile.
    """
    if data.email:
        existing = user_service.get_user_by_email(db, data.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already in use")
    return user_service.update_user(db, current_user, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (admin only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.delete_user(db, user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate a user (admin only)",
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_service.deactivate_user(db, user)
