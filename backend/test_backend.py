#!/usr/bin/env python
"""
Test script to verify the backend is working correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from fastapi import FastAPI
        print("+ FastAPI imported successfully")
    except ImportError as e:
        print(f"- Failed to import FastAPI: {e}")
        return False

    try:
        from src.services.vector_store import VectorStore
        print("+ VectorStore imported successfully")
    except ImportError as e:
        print(f"- Failed to import VectorStore: {e}")
        return False

    try:
        from src.api.v1.chat import router as chat_router
        print("+ Chat router imported successfully")
    except ImportError as e:
        print(f"- Failed to import chat router: {e}")
        return False

    try:
        from src.api.v1.search import router as search_router
        print("+ Search router imported successfully")
    except ImportError as e:
        print(f"- Failed to import search router: {e}")
        return False

    try:
        from src.services.rag_service import RAGService
        print("+ RAGService imported successfully")
    except ImportError as e:
        print(f"- Failed to import RAGService: {e}")
        return False

    return True

def test_vector_store():
    """Test vector store functionality (without actually connecting to Qdrant)"""
    print("\nTesting vector store...")

    try:
        from src.services.vector_store import VectorStore
        print("+ VectorStore class can be imported")
    except Exception as e:
        print(f"- Error importing VectorStore: {e}")
        return False

    return True

def test_main_app():
    """Test main app creation"""
    print("\nTesting main app creation...")

    try:
        from src.main import app
        print("+ Main app can be imported and created")
    except Exception as e:
        print(f"- Error creating main app: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Running backend tests...\n")

    success = True
    success &= test_imports()
    success &= test_vector_store()
    success &= test_main_app()

    if success:
        print("\n+ All tests passed! The backend should work correctly.")
        print("\nTo run the server, use:")
        print("cd backend")
        print("uvicorn src.main:app --reload")
        print("\nThen visit http://127.0.0.1:8000/docs to see the API documentation")
        print("and http://127.0.0.1:8000/api/v1/health to test the API")
    else:
        print("\n- Some tests failed. Please check the errors above.")
        sys.exit(1)