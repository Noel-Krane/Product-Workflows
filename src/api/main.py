"""
AI Research Platform - FastAPI Backend
Main application entry point with health checks and basic routing structure.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Research Platform",
    description="Multi-agent platform for strategic business research with observability",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "AI Research Platform API",
        "version": "0.1.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic health checks
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "api": "ok",
                "database": "pending",  # Will be implemented in Phase 1
                "langsmith": "pending",  # Will be implemented in Phase 1
                "openrouter": "pending"  # Will be implemented in Phase 1
            }
        }
        
        return JSONResponse(
            status_code=200,
            content=health_data
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/api/status")
async def api_status():
    """Detailed API status for dashboard."""
    return {
        "api_version": "0.1.0",
        "uptime": "just_started",  # Will implement proper uptime tracking
        "active_agents": 0,  # Will be populated from database
        "total_runs": 0,  # Will be populated from database
        "total_cost": 0.0,  # Will be populated from database
        "last_activity": None,  # Will be populated from database
        "system_status": {
            "database_connected": False,  # Will implement in Phase 1
            "langsmith_connected": False,  # Will implement in Phase 1
            "openrouter_available": False  # Will implement in Phase 1
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Please check logs"}
    )

# Placeholder routes for future implementation
@app.get("/api/agents")
async def list_agents():
    """List all available agents - placeholder for Phase 1+."""
    return {"agents": [], "message": "Agent registry coming in Phase 1"}

@app.get("/api/runs")
async def list_runs():
    """List all research runs - placeholder for Phase 1+."""
    return {"runs": [], "message": "Run history coming in Phase 1"}

@app.get("/api/costs")
async def get_costs():
    """Get cost analytics - placeholder for Phase 1+."""
    return {"total_cost": 0.0, "message": "Cost tracking coming in Phase 1"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting AI Research Platform API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )