from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.containers import Container
from app.features.admin.infrastructure.routes.admin_router import router as admin_router

container = Container()

app = FastAPI(
    title="Salud Prenatal - Admin API",
    description="API exclusiva para administradores del sistema Salud Prenatal",
    version="1.0.0",
)
app.container = container

app.include_router(admin_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "salud_prenatal_admin_backend"}
