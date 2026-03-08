from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db_session
from app.core.di.dependencies import get_current_user
from app.common.schemas.schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse, RefreshTokenRequest
)
from app.modules.auth.services.auth_service import AuthService
from app.core.config.settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db_session),
):
    service = AuthService(db)
    user = await service.register(user_data.email, user_data.username, user_data.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    service = AuthService(db)
    access_token, refresh_token, user = await service.login(credentials.email, credentials.password)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration_hours * 3600,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db_session)):
    service = AuthService(db)
    access_token = await service.get_user(request.refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration_hours * 3600,
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = AuthService(db)
    user = await service.get_user(user_id)
    return user
