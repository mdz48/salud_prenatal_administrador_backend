from typing import List, Optional

from fastapi import HTTPException, status

from app.core.enums import RoleEnum
from app.features.admin.application.ban_user_usecase import BanUserUseCase
from app.features.admin.application.delete_user_usecase import DeleteUserUseCase
from app.features.admin.application.dtos import LoginDTO
from app.features.admin.application.get_user_usecase import GetUserUseCase
from app.features.admin.application.get_users_usecase import GetUsersUseCase
from app.features.admin.application.login_admin_usecase import LoginAdminUseCase
from app.features.admin.application.unban_user_usecase import UnbanUserUseCase
from app.features.admin.infrastructure.schemas.admin_schema import AdminUserResponse, LoginResponse
from app.features.admin.infrastructure.schemas.report_schema import ReportResponseSchema
from app.features.admin.application.get_all_reports_usecase import GetAllReportsUseCase
from app.features.admin.application.get_user_reports_usecase import GetUserReportsUseCase


class AdminController:
    def __init__(
        self,
        login_admin_use_case: LoginAdminUseCase,
        get_users_use_case: GetUsersUseCase,
        get_user_use_case: GetUserUseCase,
        ban_user_use_case: BanUserUseCase,
        unban_user_use_case: UnbanUserUseCase,
        delete_user_use_case: DeleteUserUseCase,
        get_all_reports_use_case: GetAllReportsUseCase,
        get_user_reports_use_case: GetUserReportsUseCase,
    ):
        self.login_admin_use_case = login_admin_use_case
        self.get_users_use_case = get_users_use_case
        self.get_user_use_case = get_user_use_case
        self.ban_user_use_case = ban_user_use_case
        self.unban_user_use_case = unban_user_use_case
        self.delete_user_use_case = delete_user_use_case
        self.get_all_reports_use_case = get_all_reports_use_case
        self.get_user_reports_use_case = get_user_reports_use_case

    def login(self, email: str, password: str) -> LoginResponse:
        try:
            result = self.login_admin_use_case.execute(LoginDTO(email=email, password=password))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return LoginResponse(**result)

    def get_users(self, role: Optional[RoleEnum], is_active: Optional[bool]) -> List[AdminUserResponse]:
        users = self.get_users_use_case.execute(role=role, is_active=is_active)
        return [AdminUserResponse.model_validate(u) for u in users]

    def get_user(self, user_id: int) -> AdminUserResponse:
        try:
            return AdminUserResponse.model_validate(self.get_user_use_case.execute(user_id))
        except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def ban_user(self, user_id: int) -> AdminUserResponse:
        try:
            return AdminUserResponse.model_validate(self.ban_user_use_case.execute(user_id))
        except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    def unban_user(self, user_id: int) -> AdminUserResponse:
        try:
            return AdminUserResponse.model_validate(self.unban_user_use_case.execute(user_id))
        except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    def delete_user(self, user_id: int) -> AdminUserResponse:
        try:
            return AdminUserResponse.model_validate(self.delete_user_use_case.execute(user_id))
        except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    def get_all_reports(self) -> List[ReportResponseSchema]:
        reports = self.get_all_reports_use_case.execute()
        return [ReportResponseSchema.model_validate(r) for r in reports]

    def get_user_reports(self, user_id: int) -> List[ReportResponseSchema]:
        reports = self.get_user_reports_use_case.execute(user_id)
        return [ReportResponseSchema.model_validate(r) for r in reports]
