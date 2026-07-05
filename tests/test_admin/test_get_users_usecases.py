from unittest.mock import MagicMock

import pytest

from app.core.enums import RoleEnum
from app.features.admin.application.get_user_usecase import GetUserUseCase
from app.features.admin.application.get_users_usecase import GetUsersUseCase
from app.features.admin.domain.admin_user_entity import AdminUserEntity


def make_user(**overrides):
    data = dict(
        user_id=1,
        name="Paty",
        last_name="Paciente",
        email="paty@example.com",
        password="hash",
        role=RoleEnum.patient,
        is_active=True,
    )
    data.update(overrides)
    return AdminUserEntity(**data)


def test_get_users_passes_filters_to_repo():
    repo = MagicMock()
    repo.get_all.return_value = [make_user()]

    result = GetUsersUseCase(repo).execute(role=RoleEnum.patient, is_active=True)

    repo.get_all.assert_called_once_with(role=RoleEnum.patient, is_active=True)
    assert result[0].user_id == 1


def test_get_users_without_filters():
    repo = MagicMock()
    repo.get_all.return_value = []

    GetUsersUseCase(repo).execute()

    repo.get_all.assert_called_once_with(role=None, is_active=None)


def test_get_user_found():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(user_id=7)

    assert GetUserUseCase(repo).execute(7).user_id == 7


def test_get_user_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(LookupError):
        GetUserUseCase(repo).execute(999)
