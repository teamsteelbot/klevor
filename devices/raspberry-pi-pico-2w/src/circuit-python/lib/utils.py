from typing import Any, Union


def is_instance(obj: object,
                class_or_tuple: Union[type, tuple[Any, ...]]) -> None:
    """
    Check if the object is an instance of the specified class or tuple of classes.

    Args:
        obj (object): The object to check.
        class_or_tuple (Union[type, tuple[Any, ...]]): The class or tuple of classes to check against.

    Raises:
        TypeError: If the object is not an instance of the specified class or tuple of classes.
    """
    if not isinstance(obj, class_or_tuple):
        raise TypeError(
            f"Expected type {class_or_tuple}, got {type(obj)} for object {obj}"
        )