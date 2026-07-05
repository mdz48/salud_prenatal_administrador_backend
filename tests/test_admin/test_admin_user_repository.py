import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.enums import RoleEnum
from app.features.admin.infrastructure.models.user_model import Usuario
from app.features.admin.infrastructure.repositories.admin_user_repository import AdminUserRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def seed(session, email, role=RoleEnum.patient, is_active=True):
    user = Usuario(
        name="Nombre",
        last_name="Apellido",
        email=email,
        password="hash",
        role=role,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    return user


def test_get_by_email_and_id(db_session):
    seeded = seed(db_session, "a@example.com")
    repo = AdminUserRepository(db_session)

    assert repo.get_by_email("a@example.com").user_id == seeded.user_id
    assert repo.get_by_id(seeded.user_id).email == "a@example.com"
    assert repo.get_by_email("nadie@example.com") is None
    assert repo.get_by_id(9999) is None


def test_get_all_filters(db_session):
    seed(db_session, "p1@example.com", role=RoleEnum.patient, is_active=True)
    seed(db_session, "p2@example.com", role=RoleEnum.patient, is_active=False)
    seed(db_session, "d1@example.com", role=RoleEnum.doctor, is_active=True)
    repo = AdminUserRepository(db_session)

    assert len(repo.get_all()) == 3
    assert len(repo.get_all(role=RoleEnum.patient)) == 2
    assert len(repo.get_all(is_active=True)) == 2
    assert len(repo.get_all(role=RoleEnum.patient, is_active=False)) == 1


def test_set_active(db_session):
    seeded = seed(db_session, "b@example.com")
    repo = AdminUserRepository(db_session)

    assert repo.set_active(seeded.user_id, False).is_active is False
    assert repo.set_active(seeded.user_id, True).is_active is True


def test_anonymize_applies_changes(db_session):
    seeded = seed(db_session, "c@example.com")
    repo = AdminUserRepository(db_session)

    result = repo.anonymize(
        seeded.user_id,
        {
            "email": f"deleted_{seeded.user_id}@cuenta-eliminada.com",
            "name": "Usuario eliminado",
            "last_name": "",
            "phone": None,
            "image_url": None,
            "password": "deleted::x",
            "is_active": False,
        },
    )

    assert result.email == f"deleted_{seeded.user_id}@cuenta-eliminada.com"
    assert result.name == "Usuario eliminado"
    assert result.is_active is False
    # verifica la persistencia real releyendo
    assert repo.get_by_id(seeded.user_id).name == "Usuario eliminado"
