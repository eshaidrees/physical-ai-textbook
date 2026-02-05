import hashlib
import json
import time
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from collections import OrderedDict
import threading


class LRUCache:
    """
    A simple in-memory LRU (Least Recently Used) cache implementation
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the LRU cache
        :param max_size: Maximum number of items to store
        :param ttl_seconds: Time-to-live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()  # Thread-safe operations

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        """
        with self.lock:
            # Check if item exists and is not expired
            if key in self.cache:
                timestamp = self.timestamps[key]
                if time.time() - timestamp < self.ttl_seconds:
                    # Move to end (mark as recently used)
                    value = self.cache.pop(key)
                    self.cache[key] = value
                    return value
                else:
                    # Remove expired item
                    del self.cache[key]
                    del self.timestamps[key]

            return None

    def put(self, key: str, value: Any):
        """
        Put a value in the cache
        """
        with self.lock:
            # If key already exists, update it
            if key in self.cache:
                self.cache.pop(key)

            # If cache is full, remove the least recently used item
            elif len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            # Add new item
            self.cache[key] = value
            self.timestamps[key] = time.time()

    def delete(self, key: str):
        """
        Remove a specific key from the cache
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]

    def clear(self):
        """
        Clear all items from the cache
        """
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def size(self) -> int:
        """
        Get the current size of the cache
        """
        return len(self.cache)

    def keys(self) -> list:
        """
        Get all keys in the cache
        """
        with self.lock:
            # Clean up expired items first
            current_time = time.time()
            expired_keys = [
                key for key, timestamp in self.timestamps.items()
                if current_time - timestamp >= self.ttl_seconds
            ]
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]

            return list(self.cache.keys())


class CacheService:
    """
    Service to handle caching of frequently accessed data
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = LRUCache(max_size, ttl_seconds)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        self.stats_lock = threading.Lock()

    def get_cache_key(self, query: str, conversation_context: Optional[list] = None) -> str:
        """
        Generate a cache key from query and context
        """
        # Create a hash of the query and conversation context
        key_data = {
            "query": query,
            "context": conversation_context or []
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, query: str, conversation_context: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """
        Get a cached result for a query
        """
        key = self.get_cache_key(query, conversation_context)

        result = self.cache.get(key)
        with self.stats_lock:
            if result is not None:
                self.stats["hits"] += 1
            else:
                self.stats["misses"] += 1

        return result

    def set(self, query: str, conversation_context: Optional[list] = None, value: Dict[str, Any]):
        """
        Set a value in the cache
        """
        key = self.get_cache_key(query, conversation_context)
        self.cache.put(key, value)

    def delete(self, query: str, conversation_context: Optional[list] = None):
        """
        Remove a specific entry from the cache
        """
        key = self.get_cache_key(query, conversation_context)
        self.cache.delete(key)

    def clear_all(self):
        """
        Clear all cached entries
        """
        self.cache.clear()

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get cache statistics
        """
        with self.stats_lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "current_size": self.cache.size(),
                "max_size": self.cache.max_size
            }

    def cache_faq_result(self, question: str, answer: str, sources: list):
        """
        Cache a frequently asked question and its answer
        """
        cache_key = f"faq:{hashlib.sha256(question.encode()).hexdigest()}"
        faq_data = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "cached_at": datetime.now().isoformat()
        }
        self.cache.put(cache_key, faq_data)

    def get_faq_result(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached FAQ answer
        """
        cache_key = f"faq:{hashlib.sha256(question.encode()).hexdigest()}"
        return self.cache.get(cache_key)

    def cache_search_result(self, query: str, results: list):
        """
        Cache search results
        """
        cache_key = f"search:{hashlib.sha256(query.encode()).hexdigest()}"
        search_data = {
            "query": query,
            "results": results,
            "cached_at": datetime.now().isoformat()
        }
        self.cache.put(cache_key, search_data)

    def get_search_result(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search results
        """
        cache_key = f"search:{hashlib.sha256(query.encode()).hexdigest()}"
        return self.cache.get(cache_key)

    def cache_topic_summary(self, topic: str, summary: str, content: list):
        """
        Cache topic summaries
        """
        cache_key = f"topic:{hashlib.sha256(topic.encode()).hexdigest()}"
        summary_data = {
            "topic": topic,
            "summary": summary,
            "content": content,
            "cached_at": datetime.now().isoformat()
        }
        self.cache.put(cache_key, summary_data)

    def get_topic_summary(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached topic summary
        """
        cache_key = f"topic:{hashlib.sha256(topic.encode()).hexdigest()}"
        return self.cache.get(cache_key)


class FAQCacheService:
    """
    Specialized cache service for frequently asked questions
    """
    def __init__(self, max_size: int = 500, ttl_seconds: int = 7200):  # 2 hours TTL for FAQs
        self.cache_service = CacheService(max_size, ttl_seconds)

    def get_answer(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Get a cached answer for a question
        """
        return self.cache_service.get_faq_result(question)

    def cache_answer(self, question: str, answer: str, sources: list):
        """
        Cache an answer for a question
        """
        self.cache_service.cache_faq_result(question, answer, sources)

    def is_faq(self, question: str, threshold: float = 0.8) -> bool:
        """
        Determine if a question is similar to a frequently asked question
        """
        # For now, we'll just check if it's already cached
        # In a more advanced implementation, we might use similarity matching
        return self.get_answer(question) is not None


# Global cache instances
default_cache_service = CacheService(max_size=1000, ttl_seconds=3600)
faq_cache_service = FAQCacheService(max_size=500, ttl_seconds=7200)


def get_cache_service() -> CacheService:
    """
    Get the default cache service instance
    """
    return default_cache_service


def get_faq_cache_service() -> FAQCacheService:
    """
    Get the FAQ cache service instance
    """
    return faq_cache_service


def cache_query_result(query: str, conversation_context: Optional[list], result: Dict[str, Any]):
    """
    Convenience function to cache a query result
    """
    default_cache_service.set(query, conversation_context, result)


def get_cached_query_result(query: str, conversation_context: Optional[list]) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get a cached query result
    """
    return default_cache_service.get(query, conversation_context)