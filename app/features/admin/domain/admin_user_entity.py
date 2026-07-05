from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import RoleEnum


class AdminUserEntity(BaseModel):
    user_id: Optional[int] = None
    name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: RoleEnum
    is_active: bool = True
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
