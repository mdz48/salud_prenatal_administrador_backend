from typing import List, Optional

from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository


class GetUsersUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(
        self,
        role: Optional[RoleEnum] = None,
        is_active: Optional[bool] = None,
    ) -> List[AdminUserEntity]:
        return self.user_repository.get_all(role=role, is_active=is_active)
