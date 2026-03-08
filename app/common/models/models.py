from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database.connection import Base


class UserPlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    plan = Column(SQLEnum(UserPlanEnum), default=UserPlanEnum.FREE, index=True)
    daily_searches = Column(Integer, default=0)
    last_search_reset = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchEvent", back_populates="user", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    plan_type = Column(SQLEnum(UserPlanEnum), unique=True, nullable=False, index=True)
    daily_search_limit = Column(Integer, nullable=False)
    price_monthly = Column(Float, nullable=False)
    price_annual = Column(Float, nullable=False)
    features = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    renewal_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(255), index=True)
    brand = Column(String(255), index=True)
    sku = Column(String(255), unique=True, index=True, nullable=False)
    image_url = Column(String(500))
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    offers = relationship("Offer", back_populates="product", cascade="all, delete-orphan")


class Offer(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    marketplace = Column(String(100), nullable=False, index=True)
    marketplace_product_id = Column(String(255), nullable=False)
    price = Column(Float, nullable=False, index=True)
    original_price = Column(Float)
    in_stock = Column(Boolean, default=True, index=True)
    url = Column(String(500))
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    product = relationship("Product", back_populates="offers")


class SearchEvent(Base):
    __tablename__ = "search_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query = Column(String(500), nullable=False, index=True)
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    ai_router_used = Column(Boolean, default=False)
    marketplaces_searched = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    user = relationship("User", back_populates="search_history")
