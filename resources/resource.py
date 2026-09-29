"""
"""

from __future__ import annotations

from dataclasses import dataclass
from resources.resourceBuilder import ResourceBuilder

@dataclass
class ResourceData:
    """
    A class to represent a resource in an artifact.
    """
    name: str
    line_items: list[tuple[str, str]]


class Resource(ResourceData):

    builder: ResourceBuilder

    def build(self) -> str:
        return self.builder.build(self.name, self.line_items)
    
    @classmethod
    def parse(cls, full_resource_str: str):
        return cls.builder.parse(cls, full_resource_str)

