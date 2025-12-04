"""FastAPI application instance and configuration"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .routers import session, chat, history

# Create FastAPI application
app = FastAPI(
    title="Educational Support AI System",
    description="API for educational support chatbot with session management and chat history",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(history.router)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "edu-support-ai-system",
        "version": "0.1.0"
    }


@app.get("/health", tags=["health"])
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "edu-support-ai-system",
        "endpoints": {
            "init_session": "/init-session",
            "chat_sse": "/chat/sse",
            "chat_websocket": "/chat/ws/{session_id}",
            "history": "/history"
        }
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
