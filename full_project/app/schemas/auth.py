from pydantic import BaseModel


class LoginRequest(BaseModel):
    """POST /auth/login body"""
    email:    str
    password: str


class TokenResponse(BaseModel):
    """Returned after successful login"""
    access_token: str
    refresh_token: str
    token_type:   str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload"""
    email: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
