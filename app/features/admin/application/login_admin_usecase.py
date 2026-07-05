from app.core.enums import RoleEnum
from app.core.security import create_access_token, verify_password
from app.features.admin.application.dtos import LoginDTO
from app.features.admin.domain.ports import IAdminUserRepository


class LoginAdminUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(self, data: LoginDTO) -> dict:
        user = self.user_repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password):
            raise ValueError("Incorrect email or password")
        if not user.is_active:
            raise ValueError("Inactive user")
        if user.role != RoleEnum.admin:
            raise PermissionError("Operation not permitted for this role")

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id, "role": user.role.value}
        )
        return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}
