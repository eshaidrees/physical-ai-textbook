#!/usr/bin/env python
"""
Conservative script to load book content into the vector store with aggressive rate limiting
"""
import sys
import os
import time
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.vector_store import VectorStore
from src.services.content_loader import ContentLoader
from src.services.embedding_service import EmbeddingService


def load_book_content_conservative():
    """
    Load book content from the documentation directory into the vector store with aggressive rate limiting
    """
    print("Initializing vector store...")
    vector_store = VectorStore()

    print("Initializing content loader...")
    content_loader = ContentLoader(vector_store)

    # Find the docs directory
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
        print("Could not find documentation directory. Please ensure docs exist.")
        return

    print(f"Loading content from {docs_path.absolute()}...")

    # Get all markdown files
    md_files = list(docs_path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files to process")

    total_chunks_processed = 0
    total_files_processed = 0

    for file_path in md_files:
        print(f"\nProcessing file: {file_path.name}")

        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into smaller chunks to minimize API usage
            chunks = content_loader._split_content_into_chunks(content, max_chunk_size=300)
            print(f"  Split into {len(chunks)} chunks")

            # Process each chunk individually with rate limiting
            for i, chunk in enumerate(chunks):
                try:
                    # Test embedding a single chunk to make sure API works
                    embedding_service = EmbeddingService()
                    test_embedding = embedding_service.embed_query(chunk[:50] + "..." if len(chunk) > 50 else chunk)

                    # Add to vector store
                    ids = vector_store.add_texts([chunk], [{"file": file_path.name, "chunk_index": i}])
                    total_chunks_processed += 1

                    print(f"  Processed chunk {i+1}/{len(chunks)}")

                    # Longer delay between chunks to avoid rate limits
                    time.sleep(random.uniform(1.0, 2.0))

                except Exception as e:
                    print(f"  Error processing chunk {i+1}: {e}")
                    # Wait longer if there's an error
                    time.sleep(random.uniform(3.0, 5.0))
                    continue

            total_files_processed += 1
            print(f"  Completed file {file_path.name}")

            # Longer delay between files
            time.sleep(random.uniform(2.0, 3.0))

        except Exception as e:
            print(f"Error processing file {file_path.name}: {e}")
            continue

    print(f"\nCompleted! Processed {total_files_processed} files and {total_chunks_processed} content chunks.")

    # Verify the content was loaded
    stats = vector_store.get_statistics()
    print(f"Final vector store statistics: {stats}")


if __name__ == "__main__":
    load_book_content_conservative()