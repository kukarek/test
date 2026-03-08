from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserPlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro"


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    plan: UserPlanEnum
    created_at: datetime

    class Config:
        from_attributes = True


class PlanResponse(BaseModel):
    id: int
    name: str
    plan_type: UserPlanEnum
    daily_search_limit: int
    price_monthly: float


class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    is_active: bool
    started_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=500)
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: str = Field(..., max_length=255)


class ProductResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    brand: Optional[str]
    sku: str
    created_at: datetime

    class Config:
        from_attributes = True


class OfferResponse(BaseModel):
    id: int
    marketplace: str
    price: float
    in_stock: bool
    url: Optional[str]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    marketplaces: List[str] = ["wildberries", "ozon", "avito"]
    use_ai_router: bool = True
    limit: int = 20


class SearchResponse(BaseModel):
    query: str
    total_results: int
    marketplaces_searched: List[str]
    execution_time_ms: int
