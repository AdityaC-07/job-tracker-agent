"""
FastAPI Main Application
Entry point for the Job Tracker API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config.database import connect_db, disconnect_db, health_check
from api.routes import users, jobs, applications, analytics, ai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Job Tracker API",
    description="Smart Job Application Tracker with AI-powered matching and analytics",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://frontend:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred",
            "error": str(exc)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handler for ValueError exceptions
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Job Tracker API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    try:
        db_health = await health_check()
        
        return {
            "status": "healthy",
            "api": "running",
            "database": db_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# API info endpoint
@app.get("/api/info")
async def api_info():
    """
    API information endpoint
    """
    return {
        "title": "Job Tracker API",
        "version": "1.0.0",
        "description": "Smart Job Application Tracker with AI-powered matching",
        "endpoints": {
            "users": "/api/users",
            "jobs": "/api/jobs",
            "applications": "/api/applications",
            "analytics": "/api/analytics"
        },
        "features": [
            "User authentication with JWT",
            "Resume parsing (PDF/DOCX)",
            "Multi-source job search (Adzuna, JSearch, The Muse)",
            "AI-powered job matching",
            "Application tracking with Kanban board",
            "AI cover letter generation",
            "Analytics and insights",
            "Email notifications"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
