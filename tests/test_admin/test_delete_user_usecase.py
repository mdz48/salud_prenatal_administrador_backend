from unittest.mock import MagicMock

import pytest

from app.core.enums import RoleEnum
from app.features.admin.application.delete_user_usecase import (
    DeleteUserUseCase,
    deleted_email_for,
    is_deleted_email,
)
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


def test_delete_anonymizes_fields():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user()
    repo.anonymize.side_effect = lambda user_id, changes: make_user(**changes)

    result = DeleteUserUseCase(repo).execute(5)

    (called_id, changes), _ = repo.anonymize.call_args
    assert called_id == 5
    assert changes["email"] == "deleted_5@cuenta-eliminada.com"
    assert changes["name"] == "Usuario eliminado"
    assert changes["last_name"] == ""
    assert changes["phone"] is None
    assert changes["image_url"] is None
    assert changes["is_active"] is False
    assert changes["password"].startswith("deleted::")
    assert result.is_active is False


def test_delete_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(LookupError):
        DeleteUserUseCase(repo).execute(999)


def test_delete_admin_forbidden():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(role=RoleEnum.admin)

    with pytest.raises(PermissionError):
        DeleteUserUseCase(repo).execute(5)
    repo.anonymize.assert_not_called()


def test_delete_already_deleted_conflict():
    repo = MagicMock()
    repo.get_by_id.return_value = make_user(email=deleted_email_for(5), is_active=False)

    with pytest.raises(ValueError):
        DeleteUserUseCase(repo).execute(5)
    repo.anonymize.assert_not_called()


def test_is_deleted_email():
    assert is_deleted_email("deleted_9@cuenta-eliminada.com") is True
    assert is_deleted_email("paty@example.com") is False
