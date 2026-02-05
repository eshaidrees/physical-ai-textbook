#!/usr/bin/env python
"""
Script to run the RAG Chatbot API server
"""
import uvicorn
import os
import sys
from src.main import app

def main():
    # Use environment variable for port, default to 8000
    port = int(os.getenv("PORT", 8000))

    # Use environment variable for host, default to "127.0.0.1"
    host = os.getenv("HOST", "127.0.0.1")

    print(f"Starting RAG Chatbot API server on {host}:{port}")
    print(f"API documentation available at: http://{host}:{port}/docs")
    print("Press CTRL+C to stop the server")

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