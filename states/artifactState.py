"""
artifactState.py: ArtifactState class definition

uses the state design pattern to represent the various states an artifact can be in, 
such as "PLANNED", "STARTED", "BLOCKED", "COMPLETED", etc. 
This allows for more flexible and extensible handling of artifact states, as new states can be added without modifying existing code.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import ClassVar


class ArtifactState(ABC):
    """Abstract base class representing the state of an artifact"""
    
    back_reference: str
    state_registry: dict[str, type[ArtifactState]] = {}
    super_state_registry: dict[str, type[ArtifactState]] = {}
    name: ClassVar[str]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.super_state_registry[cls.name] = cls

    @abstractmethod
    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        raise NotImplementedError("is_closed method must be implemented by subclasses")
    
    @abstractmethod
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        raise NotImplementedError("is_in_work method must be implemented by subclasses")
    
    @abstractmethod
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        raise NotImplementedError("is_blocked method must be implemented by subclasses")
        