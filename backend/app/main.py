"""
Main FastAPI entry point for AI Website Builder Backend.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db
from app.db.repository import project_repo
from app.api.routes_generate import router as generate_router
from app.api.routes_projects import router as projects_router
from app.api.routes_export import router as export_router

# Initialize database schema and migrate any existing projects
init_db()
project_repo.migrate_from_json()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AI-Powered Website Builder",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router)
app.include_router(projects_router)
app.include_router(export_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "model": settings.DEFAULT_MODEL,
        "has_api_key": bool(settings.GEMINI_API_KEY)
    }

@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "has_api_key": bool(settings.GEMINI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
