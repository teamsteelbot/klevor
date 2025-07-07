from datetime import datetime as dt
from typing import Optional

from .enums import Category
from ..utils import is_instance


class Message:
    """
    Class to handle log messages.
    """

    def __init__(
        self,
        content: str,
        category: Category = Category.INFO,
        tag: Optional[str] = None
    ):
        """
        Initialize the Message class.

        Args:
            content (str): Content of the log message.
            category (Category): Category of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        self.content = content
        self.category = category
        self.tag = tag

        # Get the formatted time
        self.__formatted_time = dt.now().strftime('%H:%M:%S')

    def __str__(self):
        """
        String representation of the log message.

        Returns:
            str: The formatted log message.
        """
        if self.tag:
            return f"[{self.__formatted_time}] [{self.tag}] {self.category.name}: {self.content}"
        return f"[{self.__formatted_time}] {self.category.name}: {self.content}"

    def __repr__(self):
        """
        Representation of the log message.

        Returns:
            str: The formatted log message.
        """
        return f"Message(category={self.category}, tag={self.tag}, content={self.content})"

    @property
    def content(self) -> str:
        """
        Get the content of the log message.

        Returns:
            str: The content of the log message.
        """
        return self.__content

    @content.setter
    def content(self, content: str):
        """
        Set the content of the log message.

        Args:
            content (str): The new content for the log message.
        """
        is_instance(content, str)
        self.__content = content

    @property
    def category(self) -> Category:
        """
        Get the category of the log message.

        Returns:
            Category: The category of the log message.
        """
        return self.__category

    @category.setter
    def category(self, category: Category):
        """
        Set the category of the log message.

        Args:
            category (Category): The new category for the log message.
        """
        is_instance(category, Category)
        self.__category = category

    @property
    def tag(self) -> Optional[str]:
        """
        Get the tag of the log message.

        Returns:
            Optional[str]: The tag of the log message, or None if not set.
        """
        return self.__tag

    @tag.setter
    def tag(self, tag: Optional[str]):
        """
        Set the tag of the log message.

        Args:
            tag (Optional[str]): The new tag for the log message.
        """
        if tag:
            is_instance(tag, str)
        self.__tag = tag
