from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository
from app.features.admin.infrastructure.models.user_model import Usuario


class AdminUserRepository(IAdminUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[AdminUserEntity]:
        user_db = self.db.query(Usuario).filter(Usuario.email == email).first()
        return AdminUserEntity.model_validate(user_db) if user_db else None

    def get_by_id(self, user_id: int) -> Optional[AdminUserEntity]:
        user_db = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        return AdminUserEntity.model_validate(user_db) if user_db else None

    def get_all(
        self,
        role: Optional[RoleEnum] = None,
        is_active: Optional[bool] = None,
    ) -> List[AdminUserEntity]:
        query = self.db.query(Usuario)
        if role is not None:
            query = query.filter(Usuario.role == role)
        if is_active is not None:
            query = query.filter(Usuario.is_active == is_active)
        return [AdminUserEntity.model_validate(u) for u in query.all()]

    def set_active(self, user_id: int, is_active: bool) -> AdminUserEntity:
        user_db = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        user_db.is_active = is_active
        self.db.commit()
        self.db.refresh(user_db)
        return AdminUserEntity.model_validate(user_db)

    def anonymize(self, user_id: int, changes: dict) -> AdminUserEntity:
        user_db = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        for key, value in changes.items():
            setattr(user_db, key, value)
        self.db.commit()
        self.db.refresh(user_db)
        return AdminUserEntity.model_validate(user_db)
