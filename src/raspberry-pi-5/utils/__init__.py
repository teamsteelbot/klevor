from re import Pattern
from types import UnionType
from typing import Any
import socket

def check_type(obj: object, class_or_tuple: type | UnionType | tuple[Any, ...]) -> None:
    """
    Check if the object is an instance of the specified class or tuple of classes.
    """
    if not isinstance(obj, class_or_tuple):
        raise TypeError(
            f"Expected type {class_or_tuple}, got {type(obj)} for object {obj}"
        )


def match_any(regex_list: list[Pattern], string: str) -> bool:
    """
    Match any regex pattern in a list.

    Args:
        regex_list (list[Pattern]): List of compiled regex patterns.
        string (str): String to match against the regex patterns.
    """
    return any(regex.match(string) for regex in regex_list)


def add_single_quotes_to_list_elements(lst: list | tuple) -> list:
    """
    Add single quotes to each element in a list or tuple.
    """
    return [f"'{item}'" for item in lst]

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip