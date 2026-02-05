import uvicorn
from src.main import app

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],  # Only watch the src directory for changes
        reload_includes=["*.py"],  # Only reload on Python file changes
        reload_excludes=[],  # Don't exclude any files from watching
        workers=1,  # Use a single worker during development
        log_level="info",
        timeout_graceful_shutdown=5,  # Faster shutdown
    )