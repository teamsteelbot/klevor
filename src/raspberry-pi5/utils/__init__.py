from re import Pattern
from types import UnionType
from typing import Any


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