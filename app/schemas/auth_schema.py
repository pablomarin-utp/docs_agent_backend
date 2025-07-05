from typing import List, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    is_admin: bool
    credits: int
    created_at: datetime
    
    class Config:
        from_attributes = True