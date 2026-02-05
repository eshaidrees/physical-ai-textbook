#!/usr/bin/env python
"""
Script to properly load book content into the vector store
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.vector_store import VectorStore
from src.services.content_loader import ContentLoader
from src.services.embedding_service import EmbeddingService


def load_book_content():
    """
    Load book content from the documentation directory into the vector store
    """
    print("Initializing vector store...")
    try:
        vector_store = VectorStore()
        print("Vector store initialized successfully")
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        return False

    print("Initializing content loader...")
    content_loader = ContentLoader(vector_store)

    # Define the correct path to the book content
    docs_path = Path("../frontend_book/docs").resolve()

    if not docs_path.exists():
        print(f"Documentation directory does not exist at {docs_path}")
        # Try alternative paths
        alternative_paths = [
            Path("../../../frontend_book/docs").resolve(),
            Path("../../frontend_book/docs").resolve(),
            Path("./frontend_book/docs").resolve()
        ]

        docs_path = None
        for path in alternative_paths:
            if path.exists():
                docs_path = path
                print(f"Found documentation directory at {path}")
                break

    if docs_path is None:
        print("Could not find documentation directory. Please ensure docs exist.")
        return False

    print(f"Loading content from {docs_path}...")

    try:
        # Load content from the docs directory
        content_list = content_loader.load_book_content_from_directory(str(docs_path))
        print(f"Loaded {len(content_list)} content chunks from the book")

        if len(content_list) == 0:
            print("No content was loaded. Check if the docs directory contains .txt or .md files.")
            return False

        # Index the content into the vector store
        print("Indexing content into vector store...")
        ids = content_loader.index_content(content_list)
        print(f"Successfully indexed {len(ids)} content items into the vector store")

        # Verify the content was loaded
        stats = vector_store.get_statistics()
        print(f"Vector store statistics: {stats}")

        print("Content loading completed successfully!")
        return True

    except Exception as e:
        print(f"Error loading content: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """
    Test the vector store to ensure it's working properly
    """
    print("\nTesting vector store...")
    try:
        vector_store = VectorStore()
        stats = vector_store.get_statistics()
        print(f"Vector store statistics: {stats}")

        # Test with a sample query if there's content
        if stats.get('vectors_count', 0) > 0:
            sample_results = vector_store.similarity_search("What is ROS?", k=2)
            print(f"Sample search results: {len(sample_results)} results found")
            if sample_results:
                print(f"First result preview: {sample_results[0]['text'][:100]}...")
        else:
            print("No vectors in the store - content needs to be loaded first")

        return True
    except Exception as e:
        print(f"Error testing vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Main function to load content and test the system
    """
    print("Starting RAG chatbot content loading process...")

    # First, test the current state
    print("\n1. Testing current vector store state...")
    test_vector_store()

    # Then load the content
    print("\n2. Loading book content...")
    success = load_book_content()

    if success:
        print("\n3. Testing vector store after loading...")
        test_vector_store()
        print("\nContent loading process completed successfully!")
        return True
    else:
        print("\nContent loading process failed!")
        return False


if __name__ == "__main__":
    main()