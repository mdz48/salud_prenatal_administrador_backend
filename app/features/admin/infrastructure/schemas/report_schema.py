from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.enums import RoleEnum

class UserInfoSchema(BaseModel):
    id: int
    nombre_completo: str
    rol: str
    correo: str

class ReportResponseSchema(BaseModel):
    report_id: int
    post_id: Optional[int]
    comment_id: Optional[int]
    reason: str
    created_at: datetime
    reporter: UserInfoSchema

    class Config:
        from_attributes = True
