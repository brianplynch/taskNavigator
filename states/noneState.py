"""
"""
from __future__ import annotations
import logging
from states.artifactState import ArtifactState


class NoneState(ArtifactState):
    """Concrete class representing the state of an artifact that doesn't exist (such as a child of a childless artifact)
    States:
    - NONE
    """

    name = "NONE"

    def __new__(cls, *args, **kwargs) -> NoneState:
        # If initializing from the generic class, choose the default state
        if cls == NoneState:
            return super().__new__(NoneState)
        
        return super().__new__(cls)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        parent_class_name = super(cls).__thisclass__.__bases__[0].__name__
        if parent_class_name == "NoneState":
            cls.state_registry[cls.name] = cls
        cls.state_registry[cls.name] = cls

    def __init__(self):
        pass
