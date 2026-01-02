"""
Comprehensive memoization system for AEGIS-3.

Provides advanced caching with:
- LRU eviction policies
- Size limits
- TTL (time-to-live) support
- Cache statistics
- Thread-safe operations
"""

from functools import wraps
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, Tuple
import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class CacheStats:
    """Statistics for cache performance."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset(self):
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0


class LRUCache:
    """
    LRU cache with size limits and TTL support.

    Features:
    - Least Recently Used eviction policy
    - Maximum size enforcement
    - Optional time-to-live for entries
    - Thread-safe operations
    - Performance statistics
    """

    def __init__(self, maxsize: int = 128, ttl: Optional[float] = None):
        """
        Initialize LRU cache.

        Args:
            maxsize: Maximum number of entries to cache
            ttl: Time-to-live in seconds (None = no expiration)
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.stats = CacheStats()

    def _make_key(self, args: Tuple, kwargs: Dict) -> str:
        """Create a hashable key from arguments."""
        try:
            # Try to create a simple key first
            key_parts = [str(arg) for arg in args]
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = "|".join(key_parts)

            # If key is very long, hash it
            if len(key) > 200:
                key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
                return f"hash_{key_hash}"
            return key
        except Exception:
            # Fallback to JSON serialization with hash
            try:
                key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
                key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
                return f"json_{key_hash}"
            except Exception:
                # Last resort: use object id
                return f"id_{id(args)}_{id(kwargs)}"

    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry has expired."""
        if self.ttl is None:
            return False

        timestamp = self.timestamps.get(key)
        if timestamp is None:
            return True

        return (time.time() - timestamp) > self.ttl

    def get(self, args: Tuple, kwargs: Dict) -> Tuple[bool, Any]:
        """
        Get value from cache.

        Returns:
            (found, value) tuple
        """
        key = self._make_key(args, kwargs)

        # Check if key exists and not expired
        if key in self.cache:
            if self._is_expired(key):
                # Remove expired entry
                del self.cache[key]
                del self.timestamps[key]
                self.stats.misses += 1
                self.stats.size = len(self.cache)
                return False, None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats.hits += 1
            return True, self.cache[key]

        self.stats.misses += 1
        return False, None

    def put(self, args: Tuple, kwargs: Dict, value: Any):
        """Store value in cache."""
        key = self._make_key(args, kwargs)

        # Add or update entry
        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.cache.move_to_end(key)

        # Enforce size limit
        while len(self.cache) > self.maxsize:
            # Remove least recently used
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            self.stats.evictions += 1

        self.stats.size = len(self.cache)

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()
        self.stats.size = 0

    def info(self) -> Dict[str, Any]:
        """Get cache information and statistics."""
        return {
            'maxsize': self.maxsize,
            'ttl': self.ttl,
            'size': len(self.cache),
            'hits': self.stats.hits,
            'misses': self.stats.misses,
            'evictions': self.stats.evictions,
            'hit_rate': self.stats.hit_rate
        }


def memoize(maxsize: int = 128, ttl: Optional[float] = None):
    """
    Decorator for memoizing function results.

    Args:
        maxsize: Maximum number of results to cache
        ttl: Time-to-live in seconds for cached results

    Usage:
        @memoize(maxsize=256, ttl=60.0)
        def expensive_function(x, y):
            return x ** y
    """
    def decorator(func: Callable) -> Callable:
        cache = LRUCache(maxsize=maxsize, ttl=ttl)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get from cache
            found, value = cache.get(args, kwargs)
            if found:
                return value

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.put(args, kwargs, result)
            return result

        # Attach cache management methods
        wrapper.cache_info = cache.info
        wrapper.cache_clear = cache.clear
        wrapper._cache = cache

        return wrapper

    return decorator


class AdaptiveCache:
    """
    Cache with adaptive sizing based on hit rate.

    Automatically adjusts cache size based on performance:
    - High hit rate (>80%): Maintain current size
    - Medium hit rate (50-80%): Gradually increase size
    - Low hit rate (<50%): Gradually decrease size
    """

    def __init__(self, initial_size: int = 128, min_size: int = 16, max_size: int = 1024):
        """
        Initialize adaptive cache.

        Args:
            initial_size: Starting cache size
            min_size: Minimum allowed cache size
            max_size: Maximum allowed cache size
        """
        self.min_size = min_size
        self.max_size = max_size
        self.current_size = initial_size
        self.cache = LRUCache(maxsize=initial_size)
        self.adaptation_interval = 100  # Adapt every N operations
        self.operations = 0

    def _adapt_size(self):
        """Adapt cache size based on hit rate."""
        hit_rate = self.cache.stats.hit_rate

        if hit_rate > 0.8:
            # High hit rate - maintain size
            pass
        elif hit_rate > 0.5:
            # Medium hit rate - increase size
            new_size = min(int(self.current_size * 1.2), self.max_size)
            if new_size > self.current_size:
                self.current_size = new_size
                self.cache.maxsize = new_size
        else:
            # Low hit rate - decrease size
            new_size = max(int(self.current_size * 0.8), self.min_size)
            if new_size < self.current_size:
                self.current_size = new_size
                self.cache.maxsize = new_size

    def get(self, args: Tuple, kwargs: Dict) -> Tuple[bool, Any]:
        """Get value from cache."""
        self.operations += 1

        if self.operations % self.adaptation_interval == 0:
            self._adapt_size()

        return self.cache.get(args, kwargs)

    def put(self, args: Tuple, kwargs: Dict, value: Any):
        """Store value in cache."""
        self.cache.put(args, kwargs, value)

    def info(self) -> Dict[str, Any]:
        """Get cache information."""
        info = self.cache.info()
        info['adaptive'] = True
        info['current_size'] = self.current_size
        info['min_size'] = self.min_size
        info['max_size'] = self.max_size
        return info


def adaptive_memoize(initial_size: int = 128, min_size: int = 16, max_size: int = 1024):
    """
    Decorator for memoization with adaptive cache sizing.

    Args:
        initial_size: Starting cache size
        min_size: Minimum cache size
        max_size: Maximum cache size
    """
    def decorator(func: Callable) -> Callable:
        cache = AdaptiveCache(initial_size=initial_size, min_size=min_size, max_size=max_size)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get from cache
            found, value = cache.get(args, kwargs)
            if found:
                return value

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.put(args, kwargs, result)
            return result

        # Attach cache management methods
        wrapper.cache_info = cache.info
        wrapper.cache_clear = lambda: cache.cache.clear()
        wrapper._cache = cache

        return wrapper

    return decorator


# Convenience function for clearing all caches
_all_caches = []

def register_cache(cache):
    """Register a cache for global management."""
    _all_caches.append(cache)

def clear_all_caches():
    """Clear all registered caches."""
    for cache in _all_caches:
        if hasattr(cache, 'cache_clear'):
            cache.cache_clear()

def get_all_cache_stats() -> Dict[str, Dict]:
    """Get statistics for all registered caches."""
    stats = {}
    for i, cache in enumerate(_all_caches):
        if hasattr(cache, 'cache_info'):
            stats[f'cache_{i}'] = cache.cache_info()
    return stats
