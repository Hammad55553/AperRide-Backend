import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import decode_token
from app.models import User

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    subject = decode_token(creds.credentials)
    if not subject:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    try:
        uid = uuid.UUID(subject)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token subject")
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


async def get_current_driver(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models import Driver
    driver = (await db.execute(select(Driver).where(Driver.user_id == user.id))).scalar_one_or_none()
    if not driver:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not registered as a driver")
    return driver
