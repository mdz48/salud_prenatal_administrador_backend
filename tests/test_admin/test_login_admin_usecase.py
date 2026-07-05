from unittest.mock import MagicMock

import pytest

from app.core.enums import RoleEnum
from app.core.security import get_password_hash
from app.features.admin.application.dtos import LoginDTO
from app.features.admin.application.login_admin_usecase import LoginAdminUseCase
from app.features.admin.domain.admin_user_entity import AdminUserEntity


def make_user(**overrides):
    data = dict(
        user_id=1,
        name="Ana",
        last_name="Admin",
        email="ana@example.com",
        password=get_password_hash("secret123"),
        role=RoleEnum.admin,
        is_active=True,
    )
    data.update(overrides)
    return AdminUserEntity(**data)


def test_login_ok():
    repo = MagicMock()
    repo.get_by_email.return_value = make_user()

    result = LoginAdminUseCase(repo).execute(LoginDTO(email="ana@example.com", password="secret123"))

    assert result["token_type"] == "bearer"
    assert result["user_id"] == 1
    assert result["access_token"]


def test_login_wrong_password():
    repo = MagicMock()
    repo.get_by_email.return_value = make_user()

    with pytest.raises(ValueError):
        LoginAdminUseCase(repo).execute(LoginDTO(email="ana@example.com", password="mala"))


def test_login_unknown_email():
    repo = MagicMock()
    repo.get_by_email.return_value = None

    with pytest.raises(ValueError):
        LoginAdminUseCase(repo).execute(LoginDTO(email="x@example.com", password="secret123"))


def test_login_inactive_user():
    repo = MagicMock()
    repo.get_by_email.return_value = make_user(is_active=False)

    with pytest.raises(ValueError):
        LoginAdminUseCase(repo).execute(LoginDTO(email="ana@example.com", password="secret123"))


def test_login_non_admin_forbidden():
    repo = MagicMock()
    repo.get_by_email.return_value = make_user(role=RoleEnum.doctor)

    with pytest.raises(PermissionError):
        LoginAdminUseCase(repo).execute(LoginDTO(email="ana@example.com", password="secret123"))
