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
        def wrapper(self, *args, **kwargs):\
            # Check if the instance has a logger attribute
            if not is_instance(self, LoggerConsumerProtocol):
                raise TypeError("Instance must implement LoggerConsumerProtocol to use log_on_error decorator.")
            
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Log the error using the logger's error method
                self.logger.error(f"Error in {func.__name__}: {e}")
                raise

        return wrapper
    return decorator