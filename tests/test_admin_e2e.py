import pytest

from app.core.enums import RoleEnum
from app.core.security import get_password_hash

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def seeded_ids(app):
    from app.core.database import get_session_factory
    from app.features.admin.infrastructure.models.user_model import Usuario

    session = get_session_factory()()
    admin = Usuario(
        name="Root", last_name="Admin", email="root@admin.com",
        password=get_password_hash("admin123"), role=RoleEnum.admin, is_active=True,
    )
    patient = Usuario(
        name="Paty", last_name="Paciente", email="paty@example.com",
        password=get_password_hash("paciente123"), role=RoleEnum.patient, is_active=True,
    )
    session.add_all([admin, patient])
    session.commit()
    ids = {"admin": admin.user_id, "patient": patient.user_id}
    session.close()
    return ids


def _login(client, email, password):
    resp = client.post("/api/v1/admin/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_admin_full_flow(client, seeded_ids):
    token = _login(client, "root@admin.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    pid = seeded_ids["patient"]
    aid = seeded_ids["admin"]

    # /me
    me = client.get("/api/v1/admin/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"

    # listado con filtro por rol (query param usa el VALOR del enum)
    users = client.get("/api/v1/admin/users", params={"role": "paciente"}, headers=headers)
    assert users.status_code == 200
    assert any(u["user_id"] == pid for u in users.json())

    # detalle
    assert client.get(f"/api/v1/admin/users/{pid}", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/users/99999", headers=headers).status_code == 404

    # ban / unban
    banned = client.post(f"/api/v1/admin/users/{pid}/ban", headers=headers)
    assert banned.status_code == 200 and banned.json()["is_active"] is False
    unbanned = client.post(f"/api/v1/admin/users/{pid}/unban", headers=headers)
    assert unbanned.status_code == 200 and unbanned.json()["is_active"] is True

    # no se puede banear ni borrar a un admin
    assert client.post(f"/api/v1/admin/users/{aid}/ban", headers=headers).status_code == 403
    assert client.delete(f"/api/v1/admin/users/{aid}", headers=headers).status_code == 403

    # delete anonimiza
    deleted = client.delete(f"/api/v1/admin/users/{pid}", headers=headers)
    assert deleted.status_code == 200
    body = deleted.json()
    assert body["email"] == f"deleted_{pid}@cuenta-eliminada.com"
    assert body["name"] == "Usuario eliminado"
    assert body["phone"] is None
    assert body["is_active"] is False

    # segundo delete -> 409
    assert client.delete(f"/api/v1/admin/users/{pid}", headers=headers).status_code == 409

    # el paciente eliminado ya no puede loguearse a esta API (tampoco es admin)
    resp = client.post(
        "/api/v1/admin/login",
        data={"username": f"deleted_{pid}@cuenta-eliminada.com", "password": "paciente123"},
    )
    assert resp.status_code == 401


def test_login_rejects_non_admin(client, seeded_ids):
    # el paciente fue anonimizado en el test anterior (orden dentro del archivo);
    # sembramos uno nuevo solo para este caso
    from app.core.database import get_session_factory
    from app.features.admin.infrastructure.models.user_model import Usuario

    session = get_session_factory()()
    doc = Usuario(
        name="Doc", last_name="Tor", email="doc@example.com",
        password=get_password_hash("doctor123"), role=RoleEnum.doctor, is_active=True,
    )
    session.add(doc)
    session.commit()
    session.close()

    resp = client.post("/api/v1/admin/login", data={"username": "doc@example.com", "password": "doctor123"})
    assert resp.status_code == 403
