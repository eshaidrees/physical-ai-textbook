#!/usr/bin/env python
"""
Optimized startup script for the RAG Chatbot API
This script starts the FastAPI application with optimized settings for faster startup and reloading
"""

import uvicorn
import os
import sys
from src.main import app

def main():
    # Use environment variable for port, default to 8000
    port = int(os.getenv("PORT", 8000))

    # Use environment variable for host, default to "0.0.0.0"
    host = os.getenv("HOST", "0.0.0.0")

    # Determine if we're in development or production
    debug = os.getenv("DEBUG", "True").lower() == "true"

    if debug:
        # Development mode - enable reloading and optimized settings
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,
            reload_dirs=["src"],  # Only watch the src directory
            reload_includes=["*.py"],  # Only reload on Python file changes
            log_level="info",
            workers=1,  # Single worker for development
        )
    else:
        # Production mode - optimized for performance
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=int(os.getenv("WORKERS", 4)),
            log_level=os.getenv("LOG_LEVEL", "info"),
            timeout_keep_alive=30,
        )

if __name__ == "__main__":
    main()