from signal import SIGINT, SIG_IGN, signal
from functools import wraps

def ignore_sigint(func):
    """
    Decorator to ignore keyboard interrupts (SIGINT) in a function.

    Args:
        func (function): The function to decorate.

    Returns:
        function: The decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ignore the SIGINT signal to prevent the process from being interrupted by Ctrl+C
        signal(SIGINT, SIG_IGN)

        return func(*args, **kwargs)

    return wrapper

def log_method_error(attribute_name: str):
    """
    Decorator to log errors in a method.

    Args:
        attribute_name (str): The name of the logger attribute to use for logging errors.
    Returns:
        function: The decorated function that logs errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Try to get the logger by reflection
            logger = getattr(self, attribute_name, None)
            if logger is None:
                raise ValueError(f"Logger attribute '{attribute_name}' not found in {self.__class__.__name__}")

            # Check if the logger has an 'error' method
            if not hasattr(logger, 'error'):
                raise ValueError(f"Logger '{attribute_name}' does not have an 'error' method")

            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Log the error using the logger's error method
                logger.error(f"Error in {func.__name__}: {e}")
                raise

        return wrapper
    return decorator