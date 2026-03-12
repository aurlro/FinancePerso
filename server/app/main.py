"""
FinancePerso API - FastAPI Application
Main entry point for the backend server
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import close_db, init_db
from .routers import accounts, budgets, categories, dashboard, members, transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API metadata
API_TITLE = "FinancePerso API"
API_DESCRIPTION = """
FinancePerso API - Gestion financière personnelle

## Fonctionnalités

* **Transactions** - CRUD opérations sur les transactions
* **Catégories** - Gestion des catégories de dépenses
* **Comptes** - Gestion des comptes bancaires
* **Budgets** - Suivi des budgets mensuels
* **Dashboard** - Statistiques et analytics
* **Import** - Import CSV de transactions

## Architecture

* **Backend**: FastAPI + SQLAlchemy 2.0
* **Database**: SQLite (async via aiosqlite)
* **Validation**: Pydantic v2
* **Frontend**: React + TypeScript + Vite
"""
API_VERSION = "6.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up FinancePerso API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down FinancePerso API...")
    await close_db()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """
    Application factory.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev server
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        transactions.router,
        prefix="/api/transactions",
        tags=["Transactions"],
    )
    app.include_router(
        categories.router,
        prefix="/api/categories",
        tags=["Categories"],
    )
    app.include_router(
        accounts.router,
        prefix="/api/accounts",
        tags=["Accounts"],
    )
    app.include_router(
        budgets.router,
        prefix="/api/budgets",
        tags=["Budgets"],
    )
    app.include_router(
        members.router,
        prefix="/api/members",
        tags=["Members"],
    )
    app.include_router(
        dashboard.router,
        prefix="/api/dashboard",
        tags=["Dashboard"],
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": API_VERSION,
            "service": "financeperso-api",
        }

    # Root redirect to docs
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect root to documentation."""
        return {
            "message": "FinancePerso API",
            "version": API_VERSION,
            "docs": "/docs",
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "type": type(exc).__name__,
            },
        )

    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
