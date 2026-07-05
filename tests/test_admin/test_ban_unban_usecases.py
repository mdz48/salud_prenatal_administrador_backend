from unittest.mock import MagicMock

import pytest

from app.core.enums import RoleEnum
from app.features.admin.application.ban_user_usecase import BanUserUseCase
from app.features.admin.application.unban_user_usecase import UnbanUserUseCase
from app.features.admin.domain.admin_user_entity import AdminUserEntity


def make_user(**overrides):
    data = dict(
        user_id=5,
        name="Paty",
        last_name="Paciente",
        email="paty@example.com",
        password="hash",
        role=RoleEnum.patient,
        is_active=True,
    )
    data.update(overrides)
    return AdminUserEntity(**data)


def test_ban_sets_inactive():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user()
    repo.set_active.return_value = make_user(is_active=False)

    result = BanUserUseCase(repo).execute(5)

    repo.set_active.assert_called_once_with(5, False)
    assert result.is_active is False


def test_ban_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(LookupError):
        BanUserUseCase(repo).execute(999)


def test_ban_admin_forbidden():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(role=RoleEnum.admin)

    with pytest.raises(PermissionError):
        BanUserUseCase(repo).execute(5)
    repo.set_active.assert_not_called()


def test_unban_sets_active():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(is_active=False)
    repo.set_active.return_value = make_user(is_active=True)

    result = UnbanUserUseCase(repo).execute(5)

    repo.set_active.assert_called_once_with(5, True)
    assert result.is_active is True


def test_unban_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(LookupError):
        UnbanUserUseCase(repo).execute(999)


def test_unban_admin_forbidden():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(role=RoleEnum.admin, is_active=False)

    with pytest.raises(PermissionError):
        UnbanUserUseCase(repo).execute(5)
