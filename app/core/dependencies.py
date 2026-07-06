from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.containers import Container
from app.core.enums import RoleEnum
from app.core.security import ALGORITHM, get_secret_key
from app.features.admin.domain.admin_user_entity import AdminUserEntity
from app.features.admin.domain.ports import IAdminUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/api/v1/login")


@inject
def get_current_admin(
    token: str = Depends(oauth2_scheme),
    user_repo: IAdminUserRepository = Depends(Provide[Container.admin_user_repository]),
) -> AdminUserEntity:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_repo.get_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception
    if user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this role",
        )
    return user
