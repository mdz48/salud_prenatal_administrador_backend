# Diseño: API de Administración — Salud Prenatal

**Fecha:** 2026-07-04
**Proyecto:** `salud_prenatal_administrador_backend`
**Estado:** Aprobado

## Objetivo

API FastAPI independiente, exclusiva para usuarios administradores del sistema Salud Prenatal. Primera versión: autenticación de admins y gestión de cuentas de usuarios (listar, ver, banear, reactivar, borrar). Todos los endpoints protegidos por middleware de autenticación salvo el login.

## Contexto

- Comparte la base de datos PostgreSQL con `salud_prenatal_backend` (API principal). La tabla `users` ya existe con: `user_id`, `name` (cifrado), `last_name` (cifrado), `email`, `phone` (cifrado), `password` (bcrypt), `role` (enum: admin/paciente/doctor/recepcionista), `is_active`, `image_url`, `created_at`, `updated_at`.
- El login de la API principal ya rechaza usuarios con `is_active=False`, por lo que banear desde esta API bloquea el acceso en la principal sin cambios allá.
- Existe un skeleton previo en este proyecto con un core legacy (conexión a BD al importar, `SECRET_KEY` con fallback hardcodeado). Se reemplaza por el core moderno de la API principal.
- Hoy ningún sistema crea usuarios con `role=admin`; se necesita bootstrap.

## Decisiones

| Tema | Decisión |
|------|----------|
| Autenticación | Login propio en esta API (`POST /admin/login`). Valida contra la tabla `users` compartida, exige `role=admin` e `is_active=True`, emite JWT propio. |
| SECRET_KEY | Distinto al de la API principal. Los tokens no son intercambiables entre APIs. |
| Banear | Soft: `is_active=False`. Reversible con unban. |
| Borrar cuenta | Soft delete + anonimización: `is_active=False`, `email → deleted_{user_id}@deleted.local` (preserva unique constraint), `name`/`last_name → "Usuario eliminado"`, `phone → None`, `image_url → None`, `password →` hash aleatorio inválido. Nunca se elimina el row ni datos clínicos dependientes. |
| Anti-lockout | Ban, unban y delete rechazan operar sobre usuarios `role=admin` (incluido uno mismo) → 403. |
| Bootstrap primer admin | Script `scripts/create_admin.py`: recibe email/password por CLI, hashea con bcrypt, inserta con `role=admin`. Nada expuesto por HTTP. |
| Esquema de BD | Esta API NO ejecuta `create_all`. La API principal es dueña del esquema. Esta API solo mapea la tabla existente con su propio modelo ORM. |

## Arquitectura

Espejo de la arquitectura hexagonal/clean de la API principal:

```
salud_prenatal_administrador_backend/
├── main.py                       # FastAPI app, CORS, /health, include admin_router. SIN create_all.
├── requirements.txt
├── pytest.ini                    # marker "integration"
├── CLAUDE.md
├── scripts/
│   └── create_admin.py           # seed del primer admin
├── app/
│   ├── core/
│   │   ├── database.py           # lazy: get_engine()/get_session_factory() con @lru_cache;
│   │   │                         #   DATABASE_URL env override (tests usan SQLite);
│   │   │                         #   fallback a LOCAL_URL en fallo de conexión; get_db() generator
│   │   ├── security.py           # get_secret_key() lanza RuntimeError si falta env (sin fallback);
│   │   │                         #   verify_password/get_password_hash (bcrypt);
│   │   │                         #   create_access_token; EncryptedString con pipes lazy (@lru_cache)
│   │   ├── crypto/               # crypto_pipes.py + key_manager.py (ya existen, se conservan)
│   │   ├── enums.py              # RoleEnum con los mismos valores string que la BD compartida
│   │   ├── dependencies.py       # get_current_admin: OAuth2PasswordBearer → decodifica JWT →
│   │   │                         #   busca user por email → exige role=admin → 401/403
│   │   └── containers.py         # DeclarativeContainer, composition root único,
│   │                             #   wiring_config declarado una sola vez
│   └── features/
│       └── admin/
│           ├── domain/
│           │   ├── admin_user_entity.py   # Pydantic, sin imports de ORM:
│           │   │                          #   user_id, name, last_name, email, phone,
│           │   │                          #   role, is_active, image_url, created_at
│           │   └── ports.py               # IAdminUserRepository (Protocol):
│           │                              #   get_by_email, get_by_id, get_all(role?, is_active?),
│           │                              #   set_active(user_id, bool), anonymize(user_id, changes)
│           ├── application/
│           │   ├── dtos.py                # dataclasses de entrada (LoginDTO, UserFilterDTO...)
│           │   ├── login_admin_usecase.py
│           │   ├── get_users_usecase.py
│           │   ├── get_user_usecase.py
│           │   ├── ban_user_usecase.py
│           │   ├── unban_user_usecase.py
│           │   └── delete_user_usecase.py
│           └── infrastructure/
│               ├── models/user_model.py   # SQLAlchemy sobre tabla "users" existente,
│               │                          #   EncryptedString en name/last_name/phone
│               ├── repositories/admin_user_repository.py  # implementa el port
│               ├── schemas/admin_schema.py                # Pydantic request/response
│               ├── controllers/admin_controller.py        # schema↔entity/DTO, excepciones→HTTPException
│               └── routes/admin_router.py                 # APIRouter delgado
└── tests/
    ├── conftest.py               # setea DATABASE_URL(SQLite), SECRET_KEY, ENCRYPTION_KEY
    │                             #   ANTES de importar main
    ├── test_admin/               # unit tests: use cases con ports mockeados (MagicMock)
    └── test_smoke.py             # integration: /health + route snapshot (app.openapi()["paths"])
```

## Endpoints

Prefijo `/api/v1/admin`. Todos requieren `Depends(get_current_admin)` salvo login.

| Método | Ruta | Descripción | Errores |
|--------|------|-------------|---------|
| POST | `/login` | Email+password → JWT. Exige `role=admin`, `is_active=True`. | 401 credenciales/inactivo, 403 no-admin |
| GET | `/me` | Datos del admin autenticado. | 401 |
| GET | `/users` | Lista usuarios. Query params opcionales: `role`, `is_active`. | 401, 403 |
| GET | `/users/{user_id}` | Detalle de un usuario. | 404 |
| POST | `/users/{user_id}/ban` | `is_active=False`. | 404, 403 si target es admin |
| POST | `/users/{user_id}/unban` | `is_active=True`. | 404, 403 si target es admin |
| DELETE | `/users/{user_id}` | Soft delete + anonimización. | 404, 403 si target es admin, 409 si ya está borrado |

"Ya está borrado" se detecta por el patrón de email anonimizado (`deleted_{id}@deleted.local`).

## Flujo de datos

Router (`@inject`, recibe controller del container) → Controller (valida schema, mapea a DTO, captura excepciones de dominio → HTTPException) → Use case (`execute()`, lógica de negocio, depende solo de ports) → Repository (implementa port contra ORM, sesión del request) → PostgreSQL compartida.

Inyección de dependencias: `Container` con `providers.Resource(get_db)` → repositorio → use cases → controller, todos `providers.Factory`. Wiring declarado una vez en `wiring_config` (incluye `app.core.dependencies` y el módulo del router).

## Manejo de errores

- Use cases lanzan excepciones de dominio: `ValueError` (credenciales inválidas, regla violada), `LookupError` (no encontrado), `PermissionError` (target es admin).
- Controllers las mapean: `LookupError → 404`, `PermissionError → 403`, `ValueError → 400/401/409` según el caso.
- Los routers no contienen try/except.

## Pruebas

- **Unit:** un archivo por use case en `tests/test_admin/`, ports mockeados con `MagicMock`. Casos clave: login rechaza no-admin y inactivos; ban/delete rechazan admins; delete anonimiza los campos correctos; delete de usuario ya borrado → error.
- **Integración** (`@pytest.mark.integration`): smoke `/health` + route snapshot de `app.openapi()["paths"]` con `EXPECTED_ROUTES` explícito.
- `conftest.py` configura env antes de importar `main` (patrón de la API principal); todo el core debe ser lazy para que funcione.

## Fuera de alcance (esta versión)

- Crear/editar usuarios desde la admin API.
- Auditoría/log de acciones administrativas.
- Paginación del listado (se agrega cuando haya volumen).
- Gestión de doctores/pacientes/citas más allá de la cuenta de usuario.
