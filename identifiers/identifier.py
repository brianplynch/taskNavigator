"""
defines the Identifier class, which is used to uniquely identify 
artifacts, clients, and other entities in the Task Navigator system. 
"""

from __future__ import annotations
from identifiers.identifierBuilder import IdentifierBuilder


class Identifier:
    """
    defines the Identifier class, which is used to uniquely identify 
    artifacts, clients, and other entities in the Task Navigator system. 
    """

    # let subclasses define their own builder for flexibility in identifier formats
    builder: IdentifierBuilder 

    primary_id: str
    index_id: int
    secondary_id: str

    def __init__(self, primary_id: str, index_id: int = 0, secondary_id: str = ""):
        self.primary_id: str = primary_id
        self.index_id: int = index_id
        self.secondary_id: str = secondary_id

    def __repr__(self) -> str:
        return self.build() if not self.is_null() else "NULL IDENT"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        
        all_elements_equal = all([
                        self.primary_id == other.primary_id,
                        self.index_id == other.index_id,
                        self.secondary_id == other.secondary_id]
            )
        return all_elements_equal

    @classmethod
    def null(cls) -> Identifier:
        return cls("")
    
    @classmethod
    def new(cls, all_identifiers: list[Identifier], primary_id: str, secondary_id: str = ""):
        proposed_primary_id = cls.preserved_title_case(primary_id)
        for index_id in range(999):
            proposed_ident = cls(proposed_primary_id, index_id, secondary_id)
            if proposed_ident.is_available(all_identifiers):
                return proposed_ident
        raise RuntimeError(f"{index_id=} cannot exceed 999")

    def is_null(self) -> bool:
        """Check if the identifier is a null identifier (all attributes empty)"""
        return not self.primary_id

    def is_available(self, ids: list[Identifier]) -> bool:
        """Check if the identifier is available for use.
        """
        return self not in ids

    def build(self) -> str:
        """Build the identifier object from its components.
        """
        return self.builder.build(self.primary_id, self.index_id, self.secondary_id)

    @classmethod
    def parse(cls, full_identifier_str: str) -> Identifier:
        return cls.builder.parse(cls, full_identifier_str)

    def is_valid(self) -> bool:
        """Check if the identifier is valid according to predefined rules.
        """
        return self.builder.is_valid(self.primary_id, self.index_id, self.secondary_id)

    def build_reference(self) -> str:
        """Return a string reference to the identifier, which can be used in markdown or other contexts.
        """
        return self.builder.build_reference(self.primary_id, self.index_id, self.secondary_id)

    def build_path(self) -> str:
        """Return the identifier as a string representing a path.
        """
        return self.builder.build_path(self.primary_id, self.index_id, self.secondary_id)

    @classmethod
    def parse_reference(cls, reference_str: str) -> Identifier:
        """Parse a string reference to extract the identifier components.
        """
        return cls.builder.parse_reference(cls, reference_str)

    @staticmethod
    def preserved_title_case(text: str) -> str:
        """Returns a string in title case but any letters that are already upper case remain upper case"""
        return "".join(map(min,zip(text, text.title())))