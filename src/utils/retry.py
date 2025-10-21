"""
Retry utilities with exponential backoff

Provides decorators and utilities for retrying failed operations,
particularly useful for LLM API calls that may timeout or fail temporarily.
"""
import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Tuple, Type, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


def exponential_backoff_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    fallback_value: Optional[any] = None,
    log_attempts: bool = True
):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 30.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        exceptions: Tuple of exception types to catch (default: all exceptions)
        fallback_value: Value to return if all retries fail (default: None, which re-raises)
        log_attempts: Whether to log retry attempts (default: True)

    Returns:
        Decorated function with retry logic

    Example:
        @exponential_backoff_retry(max_attempts=3, initial_delay=2.0)
        def call_llm_api(text):
            return llm_client.analyze(text)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    if log_attempts and attempt > 1:
                        logger.info(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__}"
                        )

                    result = func(*args, **kwargs)

                    if log_attempts and attempt > 1:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt}")

                    return result

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        # Final attempt failed
                        if log_attempts:
                            logger.error(
                                f"{func.__name__} failed after {max_attempts} attempts: {e}"
                            )

                        if fallback_value is not None:
                            logger.warning(
                                f"Returning fallback value for {func.__name__}"
                            )
                            return fallback_value
                        else:
                            raise

                    # Calculate next delay with exponential backoff
                    if log_attempts:
                        logger.warning(
                            f"{func.__name__} attempt {attempt} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )

                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

            # Should never reach here, but for type safety
            if fallback_value is not None:
                return fallback_value
            raise last_exception

        return wrapper

    return decorator


def retry_on_timeout(
    max_attempts: int = 3,
    timeout_delay: float = 2.0,
    log_attempts: bool = True
):
    """
    Decorator specifically for timeout errors

    Args:
        max_attempts: Maximum number of retry attempts
        timeout_delay: Delay between retries in seconds
        log_attempts: Whether to log retry attempts

    Example:
        @retry_on_timeout(max_attempts=3, timeout_delay=5.0)
        def slow_operation():
            return expensive_llm_call()
    """
    return exponential_backoff_retry(
        max_attempts=max_attempts,
        initial_delay=timeout_delay,
        max_delay=timeout_delay,  # Fixed delay for timeouts
        exponential_base=1.0,  # No exponential increase
        exceptions=(TimeoutError, ConnectionError, OSError),
        log_attempts=log_attempts
    )


class RetryStrategy:
    """
    Configurable retry strategy for more complex retry scenarios

    Provides more control over retry behavior than the decorator
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry strategy

        Args:
            max_attempts: Maximum number of attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delays (prevents thundering herd)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute function with retry strategy

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Last exception if all attempts fail
        """
        import random

        last_exception = None
        delay = self.initial_delay

        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt == self.max_attempts:
                    logger.error(f"All {self.max_attempts} attempts failed")
                    raise

                # Calculate delay with optional jitter
                actual_delay = delay
                if self.jitter:
                    # Add ±25% jitter
                    jitter_amount = delay * 0.25
                    actual_delay = delay + random.uniform(-jitter_amount, jitter_amount)

                logger.warning(
                    f"Attempt {attempt} failed: {e}. "
                    f"Retrying in {actual_delay:.2f}s..."
                )

                time.sleep(actual_delay)
                delay = min(delay * self.exponential_base, self.max_delay)

        # Should never reach here
        raise last_exception


def with_fallback(primary_func: Callable[..., T], fallback_func: Callable[..., T]):
    """
    Execute primary function, fall back to alternative if it fails

    Args:
        primary_func: Primary function to try
        fallback_func: Fallback function if primary fails

    Returns:
        Function that tries primary, then fallback

    Example:
        result = with_fallback(
            lambda: expensive_llm_analysis(text),
            lambda: simple_lexicon_analysis(text)
        )()
    """

    def wrapper(*args, **kwargs) -> T:
        try:
            logger.debug(f"Attempting primary function: {primary_func.__name__}")
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"Primary function {primary_func.__name__} failed: {e}. "
                f"Falling back to {fallback_func.__name__}"
            )
            return fallback_func(*args, **kwargs)

    return wrapper


# Convenience function for single retry
def retry_once(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Retry a function once if it fails

    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result

    Raises:
        Exception from second attempt if both fail
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"{func.__name__} failed, retrying once: {e}")
        return func(*args, **kwargs)
