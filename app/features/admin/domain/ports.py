from typing import List, Optional, Protocol

from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity


class IAdminUserRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[AdminUserEntity]: ...

    def get_by_id(self, user_id: int) -> Optional[AdminUserEntity]: ...

    def get_all(
        self,
        role: Optional[RoleEnum] = None,
        is_active: Optional[bool] = None,
    ) -> List[AdminUserEntity]: ...

    def set_active(self, user_id: int, is_active: bool) -> AdminUserEntity: ...
    def anonymize(self, user_id: int, changes: dict) -> AdminUserEntity: ...

    def create(self, user: AdminUserEntity) -> AdminUserEntity: ...
