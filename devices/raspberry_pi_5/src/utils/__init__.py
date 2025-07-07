import socket
from enum import Enum
from re import Pattern
from types import UnionType
from typing import Any, List


def is_instance(
    obj: object,
    class_or_tuple: type | UnionType | tuple[Any, ...]
) -> None:
    """
    Check if the object is an instance of the specified class or tuple of classes,
    unwrapping proxy objects if necessary.

    Args:
        obj (object): The object to check.
        class_or_tuple (type | UnionType | tuple[Any, ...]): The class or tuple of classes to check against.
    Raises:
        TypeError: If the object is not an instance of the specified class or tuple of classes.
    """
    # Unwrap common proxy objects (e.g., multiprocessing.Manager proxies)
    if hasattr(obj, '_getvalue'):
        obj = obj._getvalue()
    elif hasattr(obj, '_get_obj'):
        obj = obj._get_obj()

    if not isinstance(obj, class_or_tuple):
        raise TypeError(
            f"Expected type {class_or_tuple}, got {type(obj)} for object {obj}"
        )


def is_subclass(
    cls: type,
    class_or_tuple: type | UnionType | tuple[Any, ...]
) -> None:
    """
    Check if the class is a subclass of the specified class or tuple of classes.

    Args:
        cls (type): The class to check.
        class_or_tuple (type | UnionType | tuple[Any, ...]): The class or tuple of classes to check against.
    Raises:
        TypeError: If the class is not a subclass of the specified class or tuple of classes.
    """
    if not issubclass(cls, class_or_tuple):
        raise TypeError(
            f"Expected subclass of {class_or_tuple}, got {type(cls)} for class {cls}"
        )


def match_any(regex_list: List[Pattern], string: str) -> bool:
    """
    Match any regex pattern in a List.

    Args:
        regex_list (List[Pattern]): List of compiled regex patterns.
        string (str): String to match against the regex patterns.
    Returns:
        bool: True if any regex matches the string, False otherwise.
    """
    return any(regex.match(string) for regex in regex_list)


def add_single_quotes_to_list_elements(lst: List | tuple) -> List:
    """
    Add single quotes to each element in a list or tuple.

    Args:
        lst (List | tuple): List or tuple of elements to be quoted.
    Returns:
        List: List of elements with single quotes added.
    """
    return [f"'{item}'" for item in lst]


def get_local_ip() -> str | None | Any:
    """
    Get the local IP address of the machine.

    Returns:
        str: Local IP address as a string.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    except Exception:
        ip = '127.0.0.1'

    finally:
        s.close()

    return ip


def map_string_to_enum(string: str, enum_class: type[Enum]) -> Any:
    """
    Map a string to an enum class.

    Args:
        string (str): The string to map.
        enum_class (type[Enum]): The enum class to map the string to.
    Returns:
        Any: The corresponding enum value.
    Raises:
        ValueError: If the string does not match any enum value.
    """
    # Check the type of enum_class
    is_subclass(enum_class, Enum)

    try:
        return enum_class[string.upper()]

    except KeyError:
        raise ValueError(
            f"'{string}' is not a valid value for {enum_class.__name__}"
        )
