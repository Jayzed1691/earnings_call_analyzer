"""
Result caching system for expensive LLM and analysis operations
Provides significant performance improvements by avoiding redundant LLM calls
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from config.settings import settings


class ResultCache:
    """
    File-based cache for analysis results

    Features:
    - TTL-based expiration
    - Content-addressed storage (hash-based keys)
    - JSON serialization
    - Automatic cleanup of expired entries
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_seconds: Optional[int] = None,
        enabled: bool = True
    ):
        """
        Initialize result cache

        Args:
            cache_dir: Directory to store cache files (default: settings.CACHE_DIR)
            ttl_seconds: Time-to-live in seconds (default: settings.CACHE_TTL)
            enabled: Whether caching is enabled (default: settings.ENABLE_CACHING)
        """
        self.cache_dir = cache_dir or settings.CACHE_DIR
        self.ttl = timedelta(seconds=ttl_seconds or settings.CACHE_TTL)
        self.enabled = enabled and settings.ENABLE_CACHING

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, text: str, analysis_type: str) -> Optional[Any]:
        """
        Retrieve cached result if available and not expired

        Args:
            text: Input text that was analyzed
            analysis_type: Type of analysis (e.g., 'sentiment', 'complexity')

        Returns:
            Cached result or None if not found/expired
        """
        if not self.enabled:
            return None

        cache_key = self._make_key(text, analysis_type)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            cached_time = datetime.fromisoformat(data['timestamp'])

            # Check if cache entry is still valid
            if datetime.now() - cached_time < self.ttl:
                return data['result']
            else:
                # Cache expired, delete it
                cache_file.unlink(missing_ok=True)
                return None
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, delete it
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, text: str, analysis_type: str, result: Any) -> None:
        """
        Store analysis result in cache

        Args:
            text: Input text that was analyzed
            analysis_type: Type of analysis
            result: Analysis result to cache (must be JSON-serializable)
        """
        if not self.enabled:
            return

        cache_key = self._make_key(text, analysis_type)
        cache_file = self.cache_dir / f"{cache_key}.json"

        data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'text_length': len(text),
            'result': result
        }

        try:
            cache_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except (TypeError, ValueError) as e:
            # Result not serializable, skip caching
            pass

    def clear(self, analysis_type: Optional[str] = None) -> int:
        """
        Clear cache entries

        Args:
            analysis_type: If specified, only clear entries of this type

        Returns:
            Number of entries cleared
        """
        if not self.enabled:
            return 0

        cleared = 0
        for cache_file in self.cache_dir.glob("*.json"):
            if analysis_type:
                try:
                    data = json.loads(cache_file.read_text())
                    if data.get('analysis_type') == analysis_type:
                        cache_file.unlink()
                        cleared += 1
                except (json.JSONDecodeError, KeyError):
                    pass
            else:
                cache_file.unlink()
                cleared += 1

        return cleared

    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries

        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0

        removed = 0
        now = datetime.now()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                cached_time = datetime.fromisoformat(data['timestamp'])

                if now - cached_time >= self.ttl:
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted file, remove it
                cache_file.unlink()
                removed += 1

        return removed

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {'enabled': False}

        total_files = 0
        total_size = 0
        by_type = {}

        for cache_file in self.cache_dir.glob("*.json"):
            total_files += 1
            total_size += cache_file.stat().st_size

            try:
                data = json.loads(cache_file.read_text())
                analysis_type = data.get('analysis_type', 'unknown')
                by_type[analysis_type] = by_type.get(analysis_type, 0) + 1
            except (json.JSONDecodeError, KeyError):
                pass

        return {
            'enabled': True,
            'total_entries': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'ttl_seconds': self.ttl.total_seconds(),
            'by_type': by_type,
            'cache_dir': str(self.cache_dir)
        }

    @staticmethod
    def _make_key(text: str, analysis_type: str) -> str:
        """
        Generate cache key from text and analysis type

        Args:
            text: Input text
            analysis_type: Type of analysis

        Returns:
            SHA256 hash as hex string
        """
        # Normalize text (strip whitespace, lowercase for sentiment)
        normalized = text.strip()
        combined = f"{analysis_type}:{normalized}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


# Global cache instance
_global_cache = None

def get_cache() -> ResultCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ResultCache()
    return _global_cache
