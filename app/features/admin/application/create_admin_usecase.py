from app.core.enums import RoleEnum
from app.core.security import get_password_hash
from app.features.admin.application.dtos import CreateAdminDTO
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository


class CreateAdminUseCase:
    def __init__(self, user_repository: IAdminUserRepository):
        self.user_repository = user_repository

    def execute(self, dto: CreateAdminDTO) -> AdminUserEntity:
        existing_user = self.user_repository.get_by_email(dto.email)
        if existing_user:
            raise ValueError("El correo electrónico ya está en uso")

        hashed_password = get_password_hash(dto.password)
        try:
            role_enum = RoleEnum(dto.role) if isinstance(dto.role, str) else dto.role
        except ValueError:
            raise ValueError("Rol inválido")

        new_user = AdminUserEntity(
            name=dto.name,
            last_name=dto.last_name,
            email=dto.email,
            phone=dto.phone,
            password=hashed_password,
            role=role_enum,
            is_active=True
        )

        return self.user_repository.create(new_user)
