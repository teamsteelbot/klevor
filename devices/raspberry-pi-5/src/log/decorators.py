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
                # Log the error using the logger's error method
                self.logger.error(f"Error in {func.__name__}: {e}")

                print(f"Error in '{self.__class__.__name__}' class on '{func.__name__}' function: {e}")

        return wrapper
    return decorator