"""

"""

from __future__ import annotations
from identifiers.identifierBuilder import IdentifierBuilder


class MarkdownIdentifierBuilder(IdentifierBuilder):
    """Markdown Identifier: A class for representing identifiers in markdown format.
    """

    separator: str = " -"

    @classmethod
    def build(cls, primary_id: str, index_id: int = 0, secondary_id: str = "") -> str:
        """
        Return the string representation of the identifier in markdown format.
        e.g. PrimaryID -SecondaryID -IndexID
        """
        if primary_id == "":
            return ""
        
        adjusted_index_id = str(index_id).zfill(3) if index_id > 0 else ""
        parts: list[str] = [primary_id, secondary_id, adjusted_index_id]
        existing_parts: list[str] = [part for part in parts if part]

        return cls.separator.join(existing_parts)

    @classmethod
    def parse(cls, identifier_type: type, full_identifier_str: str):
        """
        Parse the full identifier string to extract the primary_id, index_id, and secondary_id components.
        The expected format is "PrimaryID -SecondaryID -IndexID.md", where SecondaryID and IndexID are optional.
        """
        parts = full_identifier_str.split(" -")

        if parts == "":
            return identifier_type("")
        
        primary_id = parts[0]

        # the index_id location depends on the number of parts in the input string
        # a split list[str] of length 0 would be invalid, as primary_id is required
        # a split list[str] of length 1 means only primary_id is provided, so index_id defaults to 0
        # a split list[str] of length 2 means primary_id and index_id are provided
        # a split list[str] of length 3 means primary_id, secondary_id, and index_id are provided
        if len(parts) == 1:
            index_id = 0
        elif len(parts) == 2:
            index_id = int(parts[1])
        elif len(parts) == 3:
            index_id = int(parts[2])
        else:
            raise ValueError("Invalid identifier format. Expected format: PrimaryID -SecondaryID -IndexID.md, where SecondaryID and IndexID are optional.")
        
        secondary_id = parts[1] if len(parts) > 2 else ""
        return identifier_type(primary_id, index_id, secondary_id)

    @classmethod
    def is_valid(cls, primary_id: str, index_id: int, secondary_id: str = "") -> bool:
        """
        Check if the identifier is valid. Validity for Markdown filenames 
        means that the primary_id and secondary_id do not contain characters that are not allowed in filenames, 
        and that the index_id is a non-negative integer.
        """

        invalid_chars = set(r'\/:*?"<>|')
        if any(char in primary_id for char in invalid_chars):
            return False
        if any(char in secondary_id for char in invalid_chars):
            return False
        if not isinstance(index_id, int) or index_id < 0:
            return False
        return True
    
    @classmethod
    def build_reference(cls, primary_id: str, index_id: int, secondary_id: str = "") -> str:
        """
        Return a string reference to the identifier, which can be used in markdown or other contexts.
        For MarkdownIdentifier, the reference is the same as the full identifier string.
        """
        if not primary_id:
            return ""
        return f"[[{cls.build(primary_id, index_id, secondary_id)}]]"
    
    @classmethod
    def build_path(cls, primary_id: str, index_id: int, secondary_id: str = "") -> str:
        """
        Return a string reference to the identifier, which can be used in markdown or other contexts.
        For MarkdownIdentifier, the reference is the same as the full identifier string.
        """
        return f"{cls.build(primary_id, index_id, secondary_id)}.md"
    
    @classmethod
    def parse_reference(cls, identifier_type: type, reference_str: str):
        """
        Parse a string reference to extract the identifier components.
        For MarkdownIdentifier, the reference is expected to be in the format "[[PrimaryID -SecondaryID -IndexID]]".
        """

        if reference_str == "":
            return cls.parse(identifier_type, "")
        
        if not (reference_str.startswith("[[") and reference_str.endswith("]]")):
            raise ValueError("Invalid reference format. Expected format: [[PrimaryID -SecondaryID -IndexID]]")
        
        full_identifier_str = reference_str.strip("[]")  # Remove the surrounding [[ and ]]
        return cls.parse(identifier_type, full_identifier_str)