#!/usr/bin/env python
"""
Script to manually load book content into the vector store
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.vector_store import VectorStore
from src.services.content_loader import ContentLoader
from pathlib import Path


def load_book_content():
    """
    Load book content from the documentation directory into the vector store
    """
    print("Initializing vector store...")
    vector_store = VectorStore()

    print("Initializing content loader...")
    content_loader = ContentLoader(vector_store)

    # Path to the book content (docs directory from frontend)
    # Try multiple possible paths
    possible_paths = [
        Path("../frontend_book/docs").resolve(),
        Path("../../frontend_book/docs").resolve(),
        Path("../../../frontend_book/docs").resolve(),
        Path("./frontend_book/docs").resolve(),
        Path("../docs").resolve(),
        Path("../../docs").resolve(),
    ]

    docs_path = None
    for path in possible_paths:
        if path.exists():
            docs_path = path
            print(f"Found documentation directory at {path.absolute()}")
            break

    if docs_path is None:
        print("Could not find documentation directory. Looking for any docs directory...")
        # If all else fails, try looking for any docs directory
        import os
        for root, dirs, files in os.walk("."):
            if "docs" in dirs:
                docs_path = Path(root) / "docs"
                print(f"Found docs directory at {docs_path.absolute()}")
                break

        if docs_path is None:
            print("Could not find documentation directory. Please ensure docs exist.")
            return

    print(f"Loading content from {docs_path.absolute()}...")

    try:
        # Load content from the docs directory
        content_list = content_loader.load_book_content_from_directory(str(docs_path))
        print(f"Loaded {len(content_list)} content chunks from the book")

        if len(content_list) == 0:
            print("No content was loaded. Check if the docs directory contains .txt or .md files.")
            return

        # Index the content into the vector store
        print("Indexing content into vector store...")
        ids = content_loader.index_content(content_list)
        print(f"Successfully indexed {len(ids)} content items into the vector store")

        # Verify the content was loaded
        stats = vector_store.get_statistics()
        print(f"Vector store statistics: {stats}")

        print("Content loading completed successfully!")

    except Exception as e:
        print(f"Error loading content: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    load_book_content()