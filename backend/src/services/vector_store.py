from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Filter, FieldCondition, MatchText, MatchValue, Range
from typing import List, Dict, Any, Optional
from ..config import settings
import uuid
import logging
from functools import lru_cache
import time


class VectorStore:
    def __init__(self, collection_name: str = "book_content"):
        if not settings.qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        # Use the proper API key field, falling back to cluster_id for backward compatibility
        api_key = settings.qdrant_api_key or settings.qdrant_cluster_id

        # Initialize Qdrant client with additional options to handle potential version/access issues
        client_params = {
            "url": settings.qdrant_url,
        }

        if api_key:
            client_params["api_key"] = api_key

        # Add timeout option (this is supported by QdrantClient)
        client_params["timeout"] = 10.0  # 10 second timeout

        # For cloud Qdrant instances, we may need to handle SSL verification
        if "qdrant.cloud" in settings.qdrant_url or "qdrant.eu" in settings.qdrant_url:
            # Cloud instances might need specific handling
            # Note: The actual parameter names might vary based on the qdrant-client version
            pass  # The url parameter should handle SSL automatically based on https://
        else:
            # Local instances can use default settings
            pass  # Default behavior should work

        self.client = QdrantClient(**client_params)
        self.collection_name = collection_name
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        """
        Create the collection if it doesn't exist
        """
        try:
            # Check if collection exists
            collection_info = self.client.get_collection(self.collection_name)
            logging.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            # Check if this is a 403 Forbidden error to provide better debugging info
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg or "unauthorized" in error_msg.lower():
                logging.error(f"Qdrant authentication error: {error_msg}")
                logging.error(f"Please verify your QDRANT_URL and API key are correct")
                logging.error(f"QDRANT_URL: {settings.qdrant_url}")
                # Don't hide the 403 error - re-raise it with more context
                raise e
            elif "404" in error_msg or "not found" in error_msg.lower():
                # For 404 - collection doesn't exist, create the collection
                logging.info(f"Collection {self.collection_name} does not exist, creating it...")
                try:
                    # Create collection with optimized settings for performance
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
                        # Additional optimization parameters
                        hnsw_config=models.HnswConfigDiff(
                            m=16,  # Increase for better accuracy
                            ef_construct=100,  # Increase for better indexing quality
                            full_scan_threshold=10000  # Optimize for the number of vectors
                        ),
                        optimizers_config=models.OptimizersConfigDiff(
                            deleted_threshold=0.2,  # Merge segments with up to 20% deleted points
                            vacuum_min_vector_number=1000,  # Only vacuum segments with at least 1000 vectors
                            default_segment_number=2,  # Start with 2 segments for better parallelism
                            max_segment_size=50000,  # Limit segment size for better memory usage
                            memmap_threshold=50000,  # Use memory mapping for larger segments
                            indexing_threshold=50000  # Index on disk after this many vectors
                        )
                    )
                    logging.info(f"Collection {self.collection_name} created successfully")
                except Exception as create_error:
                    logging.error(f"Failed to create collection {self.collection_name}: {create_error}")
                    raise create_error
            else:
                # For other errors, log and raise
                logging.error(f"Unexpected error when checking collection: {e}")
                raise e

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add texts to the vector store
        """
        from .embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        embeddings = embedding_service.create_embeddings(texts)

        # Generate unique IDs for each text
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # Prepare points for insertion
        points = []
        for i, (text, embedding, text_id) in enumerate(zip(texts, embeddings, ids)):
            payload = {
                "text": text,
                "source": metadatas[i] if metadatas and i < len(metadatas) else {}
            }
            points.append(
                models.PointStruct(
                    id=text_id,
                    vector=embedding,
                    payload=payload
                )
            )

        # Insert points into the collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    def similarity_search(self, query: str, k: int = 4, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search for a query with optional filters
        """
        from .embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        query_embedding = embedding_service.embed_query(query)

        # Build filter if provided
        qdrant_filter = None
        if filters:
            qdrant_filter = self._build_qdrant_filter(filters)

        # Perform search using the low-level REST API to bypass the FastembedMixin
        from qdrant_client.http import models
        search_results = self.client._client.http.search_api.search_points(
            collection_name=self.collection_name,
            search_request=models.SearchRequest(
                vector=query_embedding,
                limit=k,
                filter=qdrant_filter,
                with_payload=True,
                with_vector=False
            )
        )

        # Extract relevant information from results
        results = []
        # The search API returns an object with a 'result' attribute containing the actual results
        actual_results = search_results.result if hasattr(search_results, 'result') else search_results
        for result in actual_results:
            results.append({
                "text": result.payload["text"],
                "metadata": result.payload.get("source", {}),
                "score": result.score
            })

        return results

    def _build_qdrant_filter(self, filters: Dict[str, Any]) -> models.Filter:
        """
        Build a Qdrant filter from a dictionary of filters
        """
        conditions = []

        for key, value in filters.items():
            if isinstance(value, str):
                # Text match
                conditions.append(
                    models.FieldCondition(
                        key=f"source.{key}",
                        match=models.MatchText(text=value)
                    )
                )
            elif isinstance(value, list):
                # Multiple values match
                keyword_condition = models.FieldCondition(
                    key=f"source.{key}",
                    match=models.MatchAny(any=value)
                )
                conditions.append(keyword_condition)
            elif isinstance(value, dict):
                # Range filter
                if "gte" in value or "lte" in value:
                    range_condition = models.FieldCondition(
                        key=f"source.{key}",
                        range=models.Range(
                            gte=value.get("gte"),
                            lte=value.get("lte"),
                            gt=value.get("gt"),
                            lt=value.get("lt")
                        )
                    )
                    conditions.append(range_condition)

        return models.Filter(must=conditions)

    def search_with_optimized_filters(self, query: str, k: int = 4, filters: Optional[Dict[str, Any]] = None,
                                      use_prefetch: bool = True) -> List[Dict[str, Any]]:
        """
        Optimized search with filtering and prefetching for better performance
        """
        from .embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        query_embedding = embedding_service.embed_query(query)

        # Build filter if provided
        qdrant_filter = None
        if filters:
            qdrant_filter = self._build_qdrant_filter(filters)

        # Perform search with optimized parameters
        search_params = models.SearchParams(
            hnsw_ef=128,  # Increase the search accuracy (higher value = more accurate but slower)
            exact=False   # Use approximate search for better performance
        )

        # Perform search using the low-level REST API to bypass the FastembedMixin
        search_results = self.client._client.http.search_api.search_points(
            collection_name=self.collection_name,
            search_request=models.SearchRequest(
                vector=query_embedding,
                limit=k,
                filter=qdrant_filter,
                params=search_params,
                with_payload=True,
                with_vector=False  # Don't return vectors to save bandwidth
            )
        )

        # Extract relevant information from results
        results = []
        # The search API returns an object with a 'result' attribute containing the actual results
        actual_results = search_results.result if hasattr(search_results, 'result') else search_results
        for result in actual_results:
            results.append({
                "text": result.payload["text"],
                "metadata": result.payload.get("source", {}),
                "score": result.score
            })

        return results

    def batch_similarity_search(self, queries: List[str], k: int = 4) -> List[List[Dict[str, Any]]]:
        """
        Perform multiple similarity searches in a batch for better performance
        """
        from .embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        query_embeddings = [embedding_service.embed_query(query) for query in queries]

        # Perform batch search using the low-level REST API
        search_results = self.client._client.http.search_api.search_batch_points(
            collection_name=self.collection_name,
            search_batch_request=models.SearchBatchRequest(
                requests=[models.SearchRequest(
                    vector=query_embedding,
                    limit=k,
                    with_payload=True,
                    with_vector=False
                ) for query_embedding in query_embeddings]
            )
        )

        # Extract relevant information from results
        all_results = []
        # The batch search API returns an object with a 'result' attribute containing the actual results
        actual_results = search_results.result if hasattr(search_results, 'result') else search_results
        for result_batch in actual_results:
            batch_results = []
            # Each batch result also has a 'result' attribute
            actual_batch_results = result_batch.result if hasattr(result_batch, 'result') else result_batch
            for result in actual_batch_results:
                batch_results.append({
                    "text": result.payload["text"],
                    "metadata": result.payload.get("source", {}),
                    "score": result.score
                })
            all_results.append(batch_results)

        return all_results

    def create_index(self, field_name: str):
        """
        Create an index on a field to optimize search performance
        """
        try:
            # Create a keyword index for faster filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=f"source.{field_name}",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
        except Exception as e:
            logging.warning(f"Could not create index for {field_name}: {e}")

    def create_full_text_index(self, field_name: str):
        """
        Create a full-text index for better text search performance
        """
        try:
            # Create a text index for full-text search
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=f"source.{field_name}",
                field_schema=models.PayloadSchemaType.TEXT
            )
        except Exception as e:
            logging.warning(f"Could not create full-text index for {field_name}: {e}")

    def optimized_add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Optimized method to add texts with batch processing for better performance
        """
        from .embedding_service import EmbeddingService

        embedding_service = EmbeddingService()

        # Batch process embeddings
        embeddings = embedding_service.create_embeddings(texts)

        # Generate unique IDs for each text
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # Prepare points for insertion in batches
        points = []
        for i, (text, embedding, text_id) in enumerate(zip(texts, embeddings, ids)):
            payload = {
                "text": text,
                "source": metadatas[i] if metadatas and i < len(metadatas) else {}
            }
            points.append(
                models.PointStruct(
                    id=text_id,
                    vector=embedding,
                    payload=payload
                )
            )

        # Use batch upsert for better performance
        batch_size = 100  # Process in batches of 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        return ids

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics for performance monitoring
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)

            # Handle different Qdrant client versions and attribute names
            vectors_count = getattr(collection_info, "vectors_count",
                                  getattr(collection_info, "points_count", 0))
            segments_count = getattr(collection_info, "segments_count", 0)

            # Handle different attribute names for disk/ram usage
            disk_usage = getattr(collection_info, "disk_usage_bytes",
                               getattr(collection_info, "disk_usage", 0))
            ram_usage = getattr(collection_info, "ram_usage_bytes",
                              getattr(collection_info, "ram_usage", 0))

            return {
                "vectors_count": vectors_count,
                "segments_count": segments_count,
                "disk_usage": disk_usage,
                "ram_usage": ram_usage,
                "collection_name": self.collection_name
            }
        except Exception as e:
            # Return safe defaults if collection doesn't exist or has issues
            logging.warning(f"Could not get collection statistics: {e}")
            return {
                "vectors_count": 0,
                "segments_count": 0,
                "disk_usage": 0,
                "ram_usage": 0,
                "collection_name": self.collection_name
            }

    def create_optimized_collection(self, vector_size: int = 1536, distance: models.Distance = models.Distance.COSINE):
        """
        Create a collection with optimized settings for performance
        """
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass  # Collection doesn't exist, which is fine

        # Create collection with optimized parameters
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=distance),
            # Additional optimization parameters
            hnsw_config=models.HnswConfigDiff(
                m=16,  # Increase for better accuracy
                ef_construct=100,  # Increase for better indexing quality
                full_scan_threshold=10000  # Optimize for the number of vectors
            ),
            optimizers_config=models.OptimizersConfigDiff(
                deleted_threshold=0.2,  # Merge segments with up to 20% deleted points
                vacuum_min_vector_number=1000,  # Only vacuum segments with at least 1000 vectors
                default_segment_number=2,  # Start with 2 segments for better parallelism
                max_segment_size=50000,  # Limit segment size for better memory usage
                memmap_threshold=50000,  # Use memory mapping for larger segments
                indexing_threshold=50000  # Index on disk after this many vectors
            ),
            quantization_config=models.ScalarQuantization(
                scalar=models.ScalarQuantizationConfig(
                    type=models.ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True
                )
            ) if False else None  # Disable quantization for now
        )

        # Create default indexes
        self.create_index("source_file")
        self.create_index("section")
        self.create_index("chapter")
        self.create_index("topics")

    def delete_collection(self):
        """
        Delete the entire collection (use with caution)
        """
        self.client.delete_collection(self.collection_name)