from signal import signal, SIGINT, SIG_IGN


def ignore_sigint(func):
    """
    Decorator to ignore keyboard interrupts (SIGINT) in a function.

    Args:
        func (function): The function to decorate.

    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        # Ignore the SIGINT signal to prevent the process from being interrupted by Ctrl+C
        signal(SIGINT, SIG_IGN)

        return func(*args, **kwargs)

    return wrapper
