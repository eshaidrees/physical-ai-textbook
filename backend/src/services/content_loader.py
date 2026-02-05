import os
from typing import List, Dict, Any
from pathlib import Path
from .vector_store import VectorStore


class ContentLoader:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def load_book_content_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Load book content from a directory of text files
        """
        content_list = []
        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory_path} does not exist")

        # Process all text files in the directory
        for file_path in directory.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Split content into chunks to avoid embedding size limits
                chunks = self._split_content_into_chunks(content)

                for i, chunk in enumerate(chunks):
                    content_list.append({
                        "text": chunk,
                        "source": {
                            "file": file_path.name,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    })

        # Also look for markdown files
        for file_path in directory.glob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Split content into chunks to avoid embedding size limits
                chunks = self._split_content_into_chunks(content)

                for i, chunk in enumerate(chunks):
                    content_list.append({
                        "text": chunk,
                        "source": {
                            "file": file_path.name,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    })

        return content_list

    def load_book_content_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load book content from a single text file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split content into chunks to avoid embedding size limits
            chunks = self._split_content_into_chunks(content)

            content_list = []
            for i, chunk in enumerate(chunks):
                content_list.append({
                    "text": chunk,
                    "source": {
                        "file": os.path.basename(file_path),
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })

        return content_list

    def _split_content_into_chunks(self, content: str, max_chunk_size: int = 500) -> List[str]:
        """
        Split content into smaller chunks to avoid embedding size limits
        """
        # Split by paragraphs first to maintain context
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If a single paragraph is too large, split it by sentences
            if len(paragraph) > max_chunk_size:
                # Split the large paragraph by sentences
                sentences = paragraph.split('. ')
                temp_chunk = ""
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    sentence_with_period = sentence + '. ' if not sentence.endswith('.') else sentence + ' '

                    if len(temp_chunk) + len(sentence_with_period) <= max_chunk_size:
                        temp_chunk += sentence_with_period
                    else:
                        if temp_chunk.strip():
                            chunks.append(temp_chunk.strip())
                        temp_chunk = sentence_with_period

                # Add remaining content from the paragraph
                if temp_chunk.strip():
                    chunks.append(temp_chunk.strip())
            else:
                # Check if adding this paragraph exceeds the limit
                if len(current_chunk) + len(paragraph) <= max_chunk_size:
                    if current_chunk:
                        current_chunk += '\n\n' + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    # Current chunk is full, save it and start a new one
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph

        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def index_content(self, content_list: List[Dict[str, Any]]) -> List[str]:
        """
        Index content into the vector store with rate limiting handling
        """
        texts = [item["text"] for item in content_list]
        metadatas = [item["source"] for item in content_list]

        # Process in smaller batches to handle rate limits
        batch_size = 10
        all_ids = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size] if metadatas else None

            try:
                batch_ids = self.vector_store.add_texts(batch_texts, batch_metadatas)
                all_ids.extend(batch_ids)

                # Add a small delay between batches to avoid overwhelming the vector store
                import time
                time.sleep(0.1)

            except Exception as e:
                print(f"Error indexing batch {i//batch_size + 1}: {e}")
                # Continue with the next batch instead of failing completely
                continue

        return all_ids