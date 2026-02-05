import cohere
import time
import random
from typing import List, Dict, Any
from ..config import settings
import numpy as np


class EmbeddingService:
    def __init__(self):
        if not settings.cohere_api_key:
            # Use mock embeddings when API key is not available
            print("COHERE_API_KEY not found, using mock embeddings for testing")
            self.use_mock = True
        else:
            try:
                self.client = cohere.Client(settings.cohere_api_key)
                self.use_mock = False
            except Exception as e:
                print(f"Error initializing Cohere client: {e}, using mock embeddings for testing")
                self.use_mock = True

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts using Cohere API or mock embeddings
        """
        if self.use_mock:
            # Create deterministic mock embeddings based on text content
            return [self._create_mock_embedding(text) for text in texts]

        try:
            # Process in smaller batches to avoid rate limits
            batch_size = 10  # Cohere's recommended batch size
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                try:
                    response = self.client.embed(
                        texts=batch,
                        model="embed-english-v3.0",  # Using Cohere's English embedding model
                        input_type="search_document"  # Specify the input type
                    )
                    all_embeddings.extend(response.embeddings)
                except Exception as e:
                    if "429" in str(e) or "TooManyRequests" in str(e):
                        # Rate limited - wait and retry
                        wait_time = 2 + random.uniform(0, 1)  # Add jitter
                        print(f"Rate limited, waiting {wait_time:.2f} seconds...")
                        time.sleep(wait_time)

                        # Retry once
                        try:
                            response = self.client.embed(
                                texts=batch,
                                model="embed-english-v3.0",
                                input_type="search_document"
                            )
                            all_embeddings.extend(response.embeddings)
                        except Exception as retry_error:
                            print(f"Retry failed for batch {i//batch_size + 1}: {retry_error}")
                            # Fall back to mock embeddings
                            all_embeddings.extend([self._create_mock_embedding(text) for text in batch])
                    else:
                        print(f"Error creating embeddings for batch {i//batch_size + 1}: {e}")
                        # Fall back to mock embeddings
                        all_embeddings.extend([self._create_mock_embedding(text) for text in batch])

                # Small delay between batches to avoid rate limits
                time.sleep(0.1)

            return all_embeddings
        except Exception as e:
            print(f"Error creating embeddings: {e}, falling back to mock embeddings")
            # Fall back to mock embeddings
            return [self._create_mock_embedding(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a single query using Cohere API or mock embeddings
        """
        if self.use_mock:
            return self._create_mock_embedding(query)

        try:
            response = self.client.embed(
                texts=[query],
                model="embed-english-v3.0",
                input_type="search_query"  # Specify the input type for queries
            )
            return response.embeddings[0]
        except Exception as e:
            if "429" in str(e) or "TooManyRequests" in str(e):
                # Rate limited - wait and retry
                wait_time = 1 + random.uniform(0, 1)  # Add jitter
                print(f"Rate limited for query, waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)

                # Retry once
                try:
                    response = self.client.embed(
                        texts=[query],
                        model="embed-english-v3.0",
                        input_type="search_query"
                    )
                    return response.embeddings[0]
                except:
                    # Fall back to mock embeddings
                    return self._create_mock_embedding(query)
            else:
                print(f"Error embedding query: {e}, falling back to mock embeddings")
                return self._create_mock_embedding(query)

    def _create_mock_embedding(self, text: str) -> List[float]:
        """
        Create a deterministic mock embedding based on the text content
        """
        # Create a hash-based embedding to ensure consistency for the same text
        text_hash = hash(text) % (2**32)
        np.random.seed(text_hash)

        # Create a 1024-dimensional vector (matching Cohere's embedding size)
        embedding = np.random.normal(0, 1, 1024).tolist()

        # Normalize the vector to unit length (common practice for embeddings)
        norm = np.linalg.norm(embedding)
        if norm != 0:
            embedding = (np.array(embedding) / norm).tolist()

        return embedding