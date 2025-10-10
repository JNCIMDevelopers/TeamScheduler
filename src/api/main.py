"""
FastAPI application factory and main application setup.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers import schedule_router, person_router, preacher_router
from ..application.models import ErrorResponse


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Team Scheduler API",
        description="REST API for church team scheduling system",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Include routers
    app.include_router(schedule_router.router, prefix="/api/v1", tags=["schedule"])
    app.include_router(person_router.router, prefix="/api/v1", tags=["persons"])
    app.include_router(preacher_router.router, prefix="/api/v1", tags=["preachers"])

    # Global exception handler
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Invalid input", detail=str(exc), status_code=400
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logging.error(f"Unhandled exception: {exc}")
        return HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Internal server error",
                detail="An unexpected error occurred",
                status_code=500,
            ).dict(),
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "2.0.0"}

    return app


# Create app instance
app = create_app()
