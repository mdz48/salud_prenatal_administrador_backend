"""Crea un usuario administrador en la BD compartida.

Uso:
    .venv\\Scripts\\python scripts/create_admin.py --email admin@ejemplo.com --password S3creta --name Ana --last-name Lopez
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import get_session_factory
from app.core.enums import RoleEnum
from app.core.security import get_password_hash
from app.features.admin.infrastructure.models.user_model import Usuario


def main() -> int:
    parser = argparse.ArgumentParser(description="Crea un usuario administrador")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--last-name", required=True)
    args = parser.parse_args()

    session = get_session_factory()()
    try:
        if session.query(Usuario).filter(Usuario.email == args.email).first():
            print(f"Ya existe un usuario con email {args.email}")
            return 1
        admin = Usuario(
            name=args.name,
            last_name=args.last_name,
            email=args.email,
            password=get_password_hash(args.password),
            role=RoleEnum.admin,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Admin creado: user_id={admin.user_id} email={args.email}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
