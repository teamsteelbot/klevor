import traceback

from .protocols import LoggerConsumerProtocol
from functools import wraps
from ..utils import is_instance

def log_on_error():
    """
    Decorator to log errors in a method.

    Returns:
        function: The decorated function that logs errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if the instance has a logger attribute
            is_instance(self, LoggerConsumerProtocol)
            
            try:
                return func(self, *args, **kwargs)
            
            except Exception as e:  
                tb = traceback.extract_tb(e.__traceback__)
                if tb:
                    filename, lineno, _, _ = tb[-1]
                    self.logger.error(
                        f"Error in {func.__name__} at {filename}:{lineno}: {e}"
                    )
                else:
                    self.logger.error(f"Error in {func.__name__}: {e}")

        return wrapper
    return decorator