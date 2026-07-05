# CLAUDE.md

## Project

API FastAPI de administración para Salud Prenatal (`salud_prenatal_administrador_backend`). Exclusiva para usuarios `role=admin`: login, listar/ver usuarios, ban/unban y borrado suave con anonimización. Comparte la BD PostgreSQL con `salud_prenatal_backend` (la API principal).

## Commands

Todo por el venv local — nunca pip/python global.

```
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn main:app --reload --port 8001
.venv\Scripts\python -m pytest
.venv\Scripts\python -m pytest -m integration
.venv\Scripts\python scripts/create_admin.py --email ... --password ... --name ... --last-name ...
```

## Architecture

Misma arquitectura hexagonal que la API principal: `app/features/admin/{domain,application,infrastructure}`, DI en `app/core/containers.py` (composition root único, wiring declarado UNA vez), core lazy (`get_engine`/`get_session_factory` con `@lru_cache`, `DATABASE_URL` override para tests).

Reglas críticas:
- **Nunca `create_all`**: la API principal es dueña del esquema; aquí solo se mapea la tabla `users` existente (`app/features/admin/infrastructure/models/user_model.py`). `RoleEnum` en `app/core/enums.py` debe mantener nombres Y valores idénticos a los de la principal.
- **`SECRET_KEY` propio** (distinto al de la principal; tokens no intercambiables). `get_secret_key()` lanza si falta — nunca agregar fallback.
- **`ENCRYPTION_KEY` compartida** con la principal (Fernet, campos `name`/`last_name`/`phone`); si difiere, la principal no puede descifrar lo que esta API escribe.
- Borrar = soft delete + anonimización (`deleted_{id}@cuenta-eliminada.com`; dominio normal porque `EmailStr` rechaza `.local`/`.invalid`). Ban = `is_active=False`. Los use cases rechazan operar sobre admins (anti-lockout).
- `tests/conftest.py` setea env ANTES de importar `main`; los tests de integración crean el esquema SQLite en la fixture `app` (porque `main.py` no lo hace). `test_smoke.py` guarda un route snapshot — actualizar `EXPECTED_ROUTES` solo de forma deliberada.

## Spec / Plan

`docs/superpowers/specs/2026-07-04-admin-api-design.md` y `docs/superpowers/plans/2026-07-04-admin-api.md`.
