from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.containers import Container
from app.core.dependencies import get_current_admin
from app.core.enums import RoleEnum
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.infrastructure.controllers.admin_controller import AdminController
from app.features.admin.infrastructure.schemas.admin_schema import AdminUserResponse, LoginResponse
from app.features.admin.infrastructure.schemas.report_schema import ReportResponseSchema

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=LoginResponse)
@inject
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.login(email=form_data.username, password=form_data.password)


@router.get("/me", response_model=AdminUserResponse)
def get_me(current_admin: AdminUserEntity = Depends(get_current_admin)):
    return AdminUserResponse.model_validate(current_admin)


@router.get("/users", response_model=List[AdminUserResponse])
@inject
def get_users(
    role: Optional[RoleEnum] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.get_users(role=role, is_active=is_active)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
@inject
def get_user(
    user_id: int,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.get_user(user_id)


@router.post("/users/{user_id}/ban", response_model=AdminUserResponse)
@inject
def ban_user(
    user_id: int,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.ban_user(user_id)


@router.post("/users/{user_id}/unban", response_model=AdminUserResponse)
@inject
def unban_user(
    user_id: int,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.unban_user(user_id)


@router.delete("/users/{user_id}", response_model=AdminUserResponse)
@inject
def delete_user(
    user_id: int,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.delete_user(user_id)


@router.get("/reports", response_model=List[ReportResponseSchema])
@inject
def get_all_reports(
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.get_all_reports()


@router.get("/users/{user_id}/reports", response_model=List[ReportResponseSchema])
@inject
def get_user_reports(
    user_id: int,
    current_admin: AdminUserEntity = Depends(get_current_admin),
    controller: AdminController = Depends(Provide[Container.admin_controller]),
):
    return controller.get_user_reports(user_id)
