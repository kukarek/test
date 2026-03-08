from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.core.security.auth import get_current_user_id
from app.core.database.connection import get_db_session, AsyncSession
from typing import Optional

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> int:
    token = credentials.credentials
    return get_current_user_id(token)


async def get_optional_user(credentials: Optional[HTTPAuthCredentials] = Depends(security)) -> Optional[int]:
    if credentials is None:
        return None
    token = credentials.credentials
    try:
        return get_current_user_id(token)
    except HTTPException:
        return None


def get_db() -> AsyncSession:
    return Depends(get_db_session)
