from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.core.enums import RoleEnum


class AdminUserCreate(BaseModel):
    name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: RoleEnum


class AdminUserResponse(BaseModel):
    user_id: int
    name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    role: RoleEnum
    is_active: bool
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
