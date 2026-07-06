from functools import lru_cache
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

load_dotenv()

Base = declarative_base()


def _resolve_database_url() -> str:
    # DATABASE_URL overrides everything (used by tests); otherwise Postgres with LOCAL_URL fallback
    override = os.getenv("DATABASE_URL")
    if override:
        return override

    url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    try:
        probe = create_engine(url, pool_pre_ping=True)
        with probe.connect():
            pass
        probe.dispose()
        return url
    except Exception as e:
        print(f"Error al conectar a la base de datos principal: {e}")
        local_url = os.getenv("LOCAL_URL")
        if not local_url:
            raise e
        print(f"Usando LOCAL_URL: {local_url}")
        return local_url


@lru_cache
def get_engine():
    return create_engine(_resolve_database_url(), pool_pre_ping=True, pool_recycle=1800)


@lru_cache
def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


SessionLocal = scoped_session(get_session_factory())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()
