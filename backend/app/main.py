"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import research, websocket
from app.core.logging import setup_logging

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting AI Research Agent...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("📊 Database tables created")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Research Agent...")

# Create FastAPI app
app = FastAPI(
    title="AI Research Agent",
    description="An intelligent research agent that processes topics and returns structured insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Research Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )