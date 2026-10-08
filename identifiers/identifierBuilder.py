"""
"""

from abc import ABC, abstractmethod


class IdentifierBuilder(ABC):
    """IdentifierBuilder class definition
    """
    @classmethod
    @abstractmethod
    def build(cls, primary_id: str, index_id: int = 0, secondary_id: str = ""):
        """Build the identifier object from its components.
        """
        ...

    @classmethod
    @abstractmethod
    def parse(cls, identifier_type: type, full_identifier_str: str):
        ...

    @classmethod
    @abstractmethod
    def is_valid(cls, primary_id: str, index_id: int, secondary_id: str = "") -> bool:
        """Check if the identifier is valid according to predefined rules.
        """
        ...

    @classmethod
    @abstractmethod
    def build_reference(cls, primary_id: str, index_id: int, secondary_id: str = "") -> str:
        """Return a string reference to the identifier, which can be used in markdown or other contexts.
        """
        ...

    @classmethod
    @abstractmethod
    def build_path(cls, primary_id: str, index_id: int, secondary_id: str = "") -> str:
        """Return the identifier as a string representing a path.
        """
        ...

    @classmethod
    @abstractmethod
    def parse_reference(cls, identifier_type: type, reference_str: str):
        """Parse a string reference to extract the identifier components.
        """
        ...