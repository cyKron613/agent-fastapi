import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, Union
from loguru import logger
from sqlalchemy.exc import (
    DisconnectionError,
    OperationalError,
    InterfaceError,
    DatabaseError
)
from asyncpg.exceptions import (
    ConnectionDoesNotExistError,
    ConnectionFailureError,
    InterfaceError as AsyncpgInterfaceError
)
from src.main.config.manager import settings


class DatabaseRetryError(Exception):
    """Database retry exhausted exception"""
    pass


def is_connection_error(exception: Exception) -> bool:
    """
    Check if the exception is a connection-related error that should trigger a retry
    
    Args:
        exception: The exception to check
        
    Returns:
        bool: True if the exception is retryable, False otherwise
    """
    # SQLAlchemy connection errors
    if isinstance(exception, (DisconnectionError, OperationalError, InterfaceError)):
        return True
    
    # AsyncPG connection errors
    if isinstance(exception, (ConnectionDoesNotExistError, ConnectionFailureError, AsyncpgInterfaceError)):
        return True
    
    # Check error message for specific connection issues
    error_msg = str(exception).lower()
    connection_error_keywords = [
        "connection was closed",
        "connection closed",
        "connection lost",
        "connection timeout",
        "connection refused",
        "connection reset",
        "server closed the connection",
        "connection broken",
        "connection terminated",
        "connection aborted",
        "connection pool exhausted",
        "connection not available"
    ]
    
    return any(keyword in error_msg for keyword in connection_error_keywords)


def calculate_delay(attempt: int, base_delay: float, backoff_factor: float) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        backoff_factor: Exponential backoff factor
        
    Returns:
        float: Delay in seconds
    """
    return base_delay * (backoff_factor ** attempt)


def db_retry(
    max_attempts: Optional[int] = None,
    base_delay: Optional[float] = None,
    backoff_factor: Optional[float] = None,
    exceptions: Optional[tuple] = None
):
    """
    Decorator for database operations with exponential backoff retry
    
    Args:
        max_attempts: Maximum number of retry attempts (default from settings)
        base_delay: Base delay between retries in seconds (default from settings)
        backoff_factor: Exponential backoff factor (default from settings)
        exceptions: Tuple of exception types to catch (default: connection errors)
        
    Returns:
        Decorated function with retry logic
    """
    # Use settings defaults if not provided
    max_attempts = max_attempts or settings.DB_RETRY_ATTEMPTS
    base_delay = base_delay or settings.DB_RETRY_DELAY
    backoff_factor = backoff_factor or settings.DB_RETRY_BACKOFF
    
    # Default exceptions to catch
    if exceptions is None:
        exceptions = (
            DisconnectionError,
            OperationalError,
            InterfaceError,
            ConnectionDoesNotExistError,
            ConnectionFailureError,
            AsyncpgInterfaceError,
            DatabaseError
        )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    logger.warning(f"Database operation attempt {attempt + 1}/{max_attempts}: {func.__name__}")
                    result = await func(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Database operation succeeded on attempt {attempt + 1}: {func.__name__}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is a retryable error
                    if not (isinstance(e, exceptions) or is_connection_error(e)):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise e
                    
                    # Don't retry on the last attempt
                    if attempt == max_attempts - 1:
                        break
                    
                    # Calculate delay for next attempt
                    delay = calculate_delay(attempt, base_delay, backoff_factor)
                    
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_attempts}): {func.__name__} - {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
            
            # All retries exhausted
            logger.error(
                f"Database operation failed after {max_attempts} attempts: {func.__name__} - {last_exception}"
            )
            raise DatabaseRetryError(
                f"Database operation failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    logger.warning(f"Database operation attempt {attempt + 1}/{max_attempts}: {func.__name__}")
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Database operation succeeded on attempt {attempt + 1}: {func.__name__}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is a retryable error
                    if not (isinstance(e, exceptions) or is_connection_error(e)):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise e
                    
                    # Don't retry on the last attempt
                    if attempt == max_attempts - 1:
                        break
                    
                    # Calculate delay for next attempt
                    delay = calculate_delay(attempt, base_delay, backoff_factor)
                    
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_attempts}): {func.__name__} - {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Wait before retry
                    time.sleep(delay)
            
            # All retries exhausted
            logger.error(
                f"Database operation failed after {max_attempts} attempts: {func.__name__} - {last_exception}"
            )
            raise DatabaseRetryError(
                f"Database operation failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator