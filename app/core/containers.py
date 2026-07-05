from dependency_injector import containers, providers

from app.core.database import get_db
from app.features.admin.application.ban_user_usecase import BanUserUseCase
from app.features.admin.application.delete_user_usecase import DeleteUserUseCase
from app.features.admin.application.get_user_usecase import GetUserUseCase
from app.features.admin.application.get_users_usecase import GetUsersUseCase
from app.features.admin.application.login_admin_usecase import LoginAdminUseCase
from app.features.admin.application.unban_user_usecase import UnbanUserUseCase
from app.features.admin.infrastructure.controllers.admin_controller import AdminController
from app.features.admin.infrastructure.repositories.admin_user_repository import AdminUserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.core.dependencies",
            "app.features.admin.infrastructure.routes.admin_router",
        ]
    )

    db = providers.Resource(get_db)

    # Repositories
    admin_user_repository = providers.Factory(AdminUserRepository, db=db)

    # Use cases
    login_admin_use_case = providers.Factory(LoginAdminUseCase, user_repository=admin_user_repository)
    get_users_use_case = providers.Factory(GetUsersUseCase, user_repository=admin_user_repository)
    get_user_use_case = providers.Factory(GetUserUseCase, user_repository=admin_user_repository)
    ban_user_use_case = providers.Factory(BanUserUseCase, user_repository=admin_user_repository)
    unban_user_use_case = providers.Factory(UnbanUserUseCase, user_repository=admin_user_repository)
    delete_user_use_case = providers.Factory(DeleteUserUseCase, user_repository=admin_user_repository)

    # Controllers
    admin_controller = providers.Factory(
        AdminController,
        login_admin_use_case=login_admin_use_case,
        get_users_use_case=get_users_use_case,
        get_user_use_case=get_user_use_case,
        ban_user_use_case=ban_user_use_case,
        unban_user_use_case=unban_user_use_case,
        delete_user_use_case=delete_user_use_case,
    )
