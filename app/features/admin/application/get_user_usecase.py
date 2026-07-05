from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository


class GetUserUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> AdminUserEntity:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        return user
