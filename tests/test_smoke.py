import pytest

pytestmark = pytest.mark.integration


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "salud_prenatal_admin_backend"}


def test_route_snapshot(app):
    # Guardian de la superficie publica: /api/v1/... no debe cambiar sin querer.
    actual = sorted(p for p in app.openapi()["paths"] if p.startswith("/api"))
    assert actual == EXPECTED_ROUTES


def test_users_requires_token(client):
    assert client.get("/api/v1/admin/users").status_code == 401


EXPECTED_ROUTES = [
    "/api/v1/admin/login",
    "/api/v1/admin/me",
    "/api/v1/admin/users",
    "/api/v1/admin/users/{user_id}",
    "/api/v1/admin/users/{user_id}/ban",
    "/api/v1/admin/users/{user_id}/unban",
]
