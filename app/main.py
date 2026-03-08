import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import settings
from app.core.database.connection import init_db
from app.modules.auth.routes.auth_routes import router as auth_router
from app.modules.search.routes.search_routes import router as search_router
from app.modules.products.routes.product_routes import router as products_router
from app.modules.billing.routes.billing_routes import router as billing_router
from app.modules.analytics.routes.analytics_routes import router as analytics_router
from app.modules.marketplace.routes.marketplace_routes import router as marketplace_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered product search platform with modular monolithic architecture",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(products_router)
app.include_router(billing_router)
app.include_router(analytics_router)
app.include_router(marketplace_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
