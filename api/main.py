"""
Main FastAPI Application for Airport AI Agent System

Provides OpenAI-compatible chat endpoints for OpenWebUI integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.routers import chatbot_response

# Initialize logger
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Airport AI Agent API",
    version="1.0.0",
    description="Multi-agent system for Kaohsiung Airport data analysis and visualization"
)

# CORS middleware (for web frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chatbot_response.router, prefix="/v1", tags=["chat"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Airport AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "airport-swarm-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

