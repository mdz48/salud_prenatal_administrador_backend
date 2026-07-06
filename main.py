from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import SessionLocal, Base, get_engine
from app.features.admin.infrastructure.models.user_model import Usuario
from app.features.admin.infrastructure.models.report_model import ReportModel
from fastapi.middleware.cors import CORSMiddleware

from app.core.containers import Container
from app.features.admin.infrastructure.routes.admin_router import router as admin_router

container = Container()

app = FastAPI(
    title="Salud Prenatal - Admin API",
    description="API exclusiva para administradores del sistema Salud Prenatal",
    version="1.0.0",
    docs_url="/api/v1/admin/docs",
    openapi_url="/api/v1/admin/openapi.json",
    redoc_url="/api/v1/admin/redoc"
)
app.container = container

app.include_router(admin_router, prefix="/api/v1/admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    finally:
        SessionLocal.remove()



@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "salud_prenatal_admin_backend"}

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=get_engine())
