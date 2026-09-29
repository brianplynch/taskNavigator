"""
"""
from __future__ import annotations
import logging
from states.artifactState import ArtifactState
from typing import Protocol

from timeStamps.dateStamp import DateStamp


class ActivityBackReference(Protocol):
    """Protocol representing the back reference of an activity artifact state"""

    start_date: DateStamp
    complete_date: DateStamp
    def set_state(self, state: ArtifactState) -> None:...
    def send_resources_to_children(self) -> None:...
    def send_deliverables_to_children(self) -> None:...
    

class ActiveInactiveArtifactState(ArtifactState):
    """Concrete class representing the state of an activity artifact

    - ACTIVE: the activity is planned but not yet started
    - INACTIVE: the activity has been started but not yet completed
    """
    name = "ActiveInactive"

    def __new__(cls, *args, **kwargs) -> ActiveInactiveArtifactState:
        # If initializing from the generic class, choose the default state
        if cls == ActiveInactiveArtifactState:
            return super().__new__(ActiveArtifactState)
        
        return super().__new__(cls)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def __init__(self, back_reference: ActivityBackReference = None):
        if back_reference:
            self.set_backreference(back_reference)
        else:
            self.back_reference = None

    def set_backreference(self, back_reference: ActivityBackReference) -> None:
        self.back_reference = back_reference

    @classmethod
    def factory_method(cls, state_name: str, back_reference: str) -> ActiveInactiveArtifactState:
        """Factory method to create an instance of the appropriate ActiveArtifactState subclass based on the state name."""
        if state_name not in cls.state_registry:
            raise ValueError(f"Invalid state name: {state_name}")
        return cls.state_registry[state_name](back_reference)

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        raise NotImplementedError("is_closed method must be implemented by subclasses")
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        raise NotImplementedError("is_in_work method must be implemented by subclasses")
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        raise NotImplementedError("is_blocked method must be implemented by subclasses")

    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        raise NotImplementedError("activate method must be implemented by subclasses")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        raise NotImplementedError("deactivate method must be implemented by subclasses")

    


class ActiveArtifactState(ActiveInactiveArtifactState):
    name = "ACTIVE"
    
    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return True
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact state already set to ACTIVE")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        self.back_reference.set_state(InactiveArtifactState(self.back_reference))
    

class InactiveArtifactState(ActiveInactiveArtifactState):
    name = "INACTIVE"
    
    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return True
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return False
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        self.back_reference.set_state(ActiveArtifactState(self.back_reference))
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact state already set to INACTIVE")
