"""
Point d'entrée principal de l'API FinancePerso.

Architecture:
    - FastAPI avec async/await
    - SQLAlchemy 2.0 avec aiosqlite
    - JWT pour l'authentification
    - Architecture en couches (routers -> services -> repositories -> models)
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

# Import routers directly from modules to avoid circular imports
from routers.auth import router as auth_router
from routers.accounts import router as accounts_router
from routers.dashboard import router as dashboard_router
from routers.transactions import router as transactions_router

# TODO: Create these routers
# from routers.categories import router as categories_router
# from routers.budgets import router as budgets_router
# from routers.household import router as household_router
# from routers.rules import router as rules_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔗 Database: {settings.database_url}")
    
    # TODO: Initialiser la base de données et créer les tables
    # from database import init_db
    # await init_db()
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST pour l'application FinancePerso",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# CORS Middleware - Configuration permissive pour développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origins en dev
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
    expose_headers=["*"],
)

# Inclusion des routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
# app.include_router(categories_router, prefix="/api/categories", tags=["Categories"])
# app.include_router(budgets_router, prefix="/api/budgets", tags=["Budgets"])
# app.include_router(household_router, prefix="/api/household", tags=["Household"])
# app.include_router(rules_router, prefix="/api/rules", tags=["Rules"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Endpoint de vérification de santé."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/api", tags=["Root"])
async def root():
    """Page d'accueil de l'API."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
