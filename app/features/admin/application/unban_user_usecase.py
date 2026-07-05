from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository


class UnbanUserUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> AdminUserEntity:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        if user.role == RoleEnum.admin:
            raise PermissionError("Cannot modify an admin account")
        return self.user_repository.set_active(user_id, True)
