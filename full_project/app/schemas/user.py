from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.helpers import validation_error


class UserCreate(BaseModel):
    """Used when registering a new user — POST /auth/register"""
    name:     str
    email:    EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) < 2:
            validation_error("NAME_MIN")
        if len(value) > 100:
            validation_error("NAME_MAX")
        return value
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            validation_error("PASSWORD_MIN")
        if len(value) > 72:
            validation_error("PASSWORD_MAX")
        return value


class UserUpdate(BaseModel):
    """Used when updating profile — PATCH /users/me"""
    name:  Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Returned to the client — never includes password"""
    id:         int
    name:       str
    email:      str
    role:       str
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChangePassword(BaseModel):
    """Used for password change endpoint"""
    current_password: str
    new_password:     str = Field(..., min_length=6)
