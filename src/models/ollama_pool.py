"""
Ollama Connection Pool

Manages a pool of Ollama client connections for concurrent LLM requests.
Prevents connection exhaustion and improves performance under load.
"""
import logging
from typing import Optional, Dict, Any
from queue import Queue, Empty
from threading import Lock
import time
from contextlib import contextmanager

from src.models.ollama_client import OllamaClient
from config.settings import settings

logger = logging.getLogger(__name__)


class OllamaConnectionPool:
    """
    Connection pool for Ollama clients

    Features:
    - Reusable connections
    - Automatic connection recycling
    - Thread-safe operations
    - Connection health checking
    - Configurable pool size
    """

    def __init__(
        self,
        pool_size: int = 4,
        max_overflow: int = 2,
        timeout: float = 30.0,
        recycle_after: int = 100
    ):
        """
        Initialize connection pool

        Args:
            pool_size: Number of connections to maintain
            max_overflow: Additional connections allowed when pool is exhausted
            timeout: Timeout for acquiring connection (seconds)
            recycle_after: Recycle connection after N uses
        """
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        self.recycle_after = recycle_after

        # Pool management
        self._pool: Queue = Queue(maxsize=pool_size + max_overflow)
        self._lock = Lock()
        self._created_connections = 0
        self._overflow_connections = 0

        # Metrics
        self.total_requests = 0
        self.active_connections = 0
        self.pool_exhausted_count = 0

        logger.info(
            f"Initialized Ollama connection pool: "
            f"size={pool_size}, overflow={max_overflow}"
        )

        # Pre-populate pool
        self._populate_pool()

    def _populate_pool(self):
        """Pre-create connections to fill the pool"""
        with self._lock:
            for _ in range(self.pool_size):
                conn = self._create_connection()
                self._pool.put(conn)

    def _create_connection(self) -> Dict[str, Any]:
        """
        Create a new connection wrapper

        Returns:
            Dictionary with client and metadata
        """
        client = OllamaClient()
        connection = {
            'client': client,
            'created_at': time.time(),
            'use_count': 0,
            'last_used': time.time()
        }

        self._created_connections += 1
        logger.debug(f"Created connection #{self._created_connections}")

        return connection

    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager)

        Usage:
            with pool.get_connection() as client:
                result = client.analyze_sentiment(text)

        Yields:
            OllamaClient instance

        Raises:
            TimeoutError: If no connection available within timeout
        """
        connection = None
        is_overflow = False

        try:
            # Try to get connection from pool
            try:
                connection = self._pool.get(timeout=self.timeout)
                logger.debug("Acquired connection from pool")

            except Empty:
                # Pool exhausted, try to create overflow connection
                with self._lock:
                    if self._overflow_connections < self.max_overflow:
                        self._overflow_connections += 1
                        is_overflow = True
                        connection = self._create_connection()
                        logger.warning(
                            f"Pool exhausted, created overflow connection "
                            f"({self._overflow_connections}/{self.max_overflow})"
                        )
                        self.pool_exhausted_count += 1
                    else:
                        raise TimeoutError(
                            f"Connection pool exhausted and max overflow reached. "
                            f"Pool size: {self.pool_size}, "
                            f"Overflow: {self.max_overflow}"
                        )

            # Update metrics
            self.total_requests += 1
            self.active_connections += 1

            # Check if connection needs recycling
            if connection['use_count'] >= self.recycle_after:
                logger.info(
                    f"Recycling connection after {connection['use_count']} uses"
                )
                connection = self._create_connection()

            # Update connection metadata
            connection['use_count'] += 1
            connection['last_used'] = time.time()

            # Yield the client
            yield connection['client']

        finally:
            # Return connection to pool
            if connection is not None:
                self.active_connections -= 1

                if is_overflow:
                    # Don't return overflow connections to pool
                    with self._lock:
                        self._overflow_connections -= 1
                    logger.debug("Discarded overflow connection")
                else:
                    # Return to pool
                    try:
                        self._pool.put_nowait(connection)
                        logger.debug("Returned connection to pool")
                    except Exception as e:
                        logger.error(f"Failed to return connection to pool: {e}")

    def get_client(self) -> OllamaClient:
        """
        Get a client from the pool (non-context manager version)

        Note: Caller is responsible for returning via return_client()

        Returns:
            Tuple of (OllamaClient, connection_wrapper)
        """
        try:
            connection = self._pool.get(timeout=self.timeout)
            self.active_connections += 1
            self.total_requests += 1
            connection['use_count'] += 1
            connection['last_used'] = time.time()
            return connection['client'], connection

        except Empty:
            raise TimeoutError("Connection pool exhausted")

    def return_client(self, connection: Dict[str, Any]):
        """
        Return a client to the pool

        Args:
            connection: Connection wrapper from get_client()
        """
        self.active_connections -= 1
        self._pool.put(connection)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pool statistics

        Returns:
            Dictionary with pool metrics
        """
        return {
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'active_connections': self.active_connections,
            'available_connections': self._pool.qsize(),
            'total_requests': self.total_requests,
            'pool_exhausted_count': self.pool_exhausted_count,
            'created_connections': self._created_connections,
            'overflow_connections': self._overflow_connections
        }

    def health_check(self) -> bool:
        """
        Perform health check on pool

        Returns:
            True if pool is healthy
        """
        try:
            with self.get_connection() as client:
                # Try a simple operation
                client.check_model_availability(settings.SENTIMENT_MODEL)
            return True
        except Exception as e:
            logger.error(f"Pool health check failed: {e}")
            return False

    def shutdown(self):
        """Shutdown the connection pool and cleanup resources"""
        logger.info("Shutting down Ollama connection pool")

        # Drain the pool
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                # Cleanup connection if needed
                # (OllamaClient doesn't have explicit cleanup currently)
            except Empty:
                break

        logger.info(
            f"Pool shutdown complete. "
            f"Total requests served: {self.total_requests}"
        )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
        return False


# Global connection pool instance
_global_pool: Optional[OllamaConnectionPool] = None
_pool_lock = Lock()


def get_pool(
    pool_size: Optional[int] = None,
    max_overflow: Optional[int] = None
) -> OllamaConnectionPool:
    """
    Get or create global connection pool

    Args:
        pool_size: Pool size (default: from settings or 4)
        max_overflow: Max overflow (default: half of pool_size)

    Returns:
        Global OllamaConnectionPool instance
    """
    global _global_pool

    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:  # Double-check locking
                pool_size = pool_size or getattr(
                    settings,
                    'OLLAMA_POOL_SIZE',
                    4
                )
                max_overflow = max_overflow or max(1, pool_size // 2)

                _global_pool = OllamaConnectionPool(
                    pool_size=pool_size,
                    max_overflow=max_overflow
                )

    return _global_pool


def reset_pool():
    """Reset the global pool (useful for testing)"""
    global _global_pool

    with _pool_lock:
        if _global_pool is not None:
            _global_pool.shutdown()
            _global_pool = None
