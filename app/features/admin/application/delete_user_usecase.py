import secrets

from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository

DELETED_EMAIL_DOMAIN = "cuenta-eliminada.com"


def deleted_email_for(user_id: int) -> str:
    return f"deleted_{user_id}@{DELETED_EMAIL_DOMAIN}"


def is_deleted_email(email: str) -> bool:
    return email.endswith(f"@{DELETED_EMAIL_DOMAIN}")


class DeleteUserUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> AdminUserEntity:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        if user.role == RoleEnum.admin:
            raise PermissionError("Cannot delete an admin account")
        if is_deleted_email(user.email):
            raise ValueError("User is already deleted")

        changes = {
            "email": deleted_email_for(user_id),
            "name": "Usuario eliminado",
            "last_name": "",
            "phone": None,
            "image_url": None,
            # token aleatorio, jamas verificara como hash bcrypt valido
            "password": f"deleted::{secrets.token_urlsafe(32)}",
            "is_active": False,
        }
        return self.user_repository.anonymize(user_id, changes)
