from fastapi import FastAPI
from .services.vector_store import VectorStore
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.chat import router as chat_router
from .api.v1.search import router as search_router
from .api.v1.health import router as health_router
from .middleware.security import security_middleware, add_security_headers
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Chatbot API",
    description="API for Physical AI & Humanoid Robotics Book",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

vector_store = VectorStore()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers that the frontend might need
    expose_headers=["Access-Control-Allow-Origin"]
)

# Add security middleware
app.middleware("http")(security_middleware)

# Add security headers to all responses
@app.middleware("http")
async def add_security_headers_middleware(request, call_next):
    response = await call_next(request)
    response = add_security_headers(response)
    return response

# Include API routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Chatbot API for Physical AI & Humanoid Robotics Book"}

@app.on_event("startup")
async def startup_event():
    """Initialize vector store and load content on startup"""
    logger.info("Application starting up...")
    try:
        # Import here to avoid circular imports and only when needed
        from .services.vector_store import VectorStore
        from .services.content_loader import ContentLoader
        from pathlib import Path

        # Initialize vector store
        vector_store = VectorStore()

        # Check if content has already been loaded
        try:
            stats = vector_store.get_statistics()
            logger.info(f"Vector store stats: {stats}")
        except Exception as e:
            logger.warning(f"Could not get vector store statistics: {e}")

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )