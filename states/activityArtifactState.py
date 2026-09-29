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
    def set_state(self, state: ActivityArtifactState) -> None:...
    def send_resources_to_children(self) -> None:...
    def send_deliverables_to_children(self) -> None:...
    

def start_activity(back_reference: ActivityBackReference) -> None:
    """Starts an activity artifact by setting its state to STARTED and sending resources and deliverables to its children."""
    with back_reference as artifact:
        artifact.set_state(StartedActivityArtifactState(artifact))
    with back_reference as artifact:
        artifact.started = DateStamp.today()
    with back_reference as artifact:
        artifact.send_resources_to_children()


def complete_activity(back_reference: ActivityBackReference) -> None:
    """Completes an activity artifact by setting its state to COMPLETED and sending deliverables to its children."""
    with back_reference as artifact:
        artifact.set_state(CompletedActivityArtifactState(artifact))
    with back_reference as artifact:
        artifact.completed = DateStamp.today()
    with back_reference as artifact:
        artifact.send_deliverables_to_children()
    


class ActivityArtifactState(ArtifactState):
    """Concrete class representing the state of an activity artifact

    - PLANNED: the activity is planned but not yet started
    - STARTED: the activity has been started but not yet completed
    - CONTINUAL: the activity is ongoing and will not be completed until a later date
    - BLOCKED: the activity is blocked and cannot be started or completed
    - CANCELED: the activity has been canceled and will not be completed
    - REASSIGNED: the activity has been reassigned to another person and will not be completed by the original assignee
    - COMPLETED: the activity has been completed
    
    """

    name = "ACTIVITY"

    def __new__(cls, *args, **kwargs) -> ActivityArtifactState:
        # If initializing from the generic class, choose the default state
        if cls == ActivityArtifactState:
            return super().__new__(PlannedActivityArtifactState)
        
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
    def factory_method(cls, state_name: str, back_reference: str) -> ActivityArtifactState:
        """Factory method to create an instance of the appropriate ActivityArtifactState subclass based on the state name."""
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

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        raise NotImplementedError("plan method must be implemented by subclasses")
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        raise NotImplementedError("start method must be implemented by subclasses")
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        raise NotImplementedError("continual method must be implemented by subclasses")

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        raise NotImplementedError("block method must be implemented by subclasses")
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        raise NotImplementedError("cancel method must be implemented by subclasses")
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        raise NotImplementedError("reassign method must be implemented by subclasses")
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        raise NotImplementedError("complete method must be implemented by subclasses")
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        raise NotImplementedError("activate method must be implemented by subclasses")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        raise NotImplementedError("deactivate method must be implemented by subclasses")


class PlannedActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the PLANNED state of an activity artifact"""

    name = "PLANNED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls
    
    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return False
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state already set to PLANNED")
        # do nothing since the artifact is already in the PLANNED state
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        complete_activity(self.back_reference)
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")

    

class StartedActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the STARTED state of an activity artifact"""

    name = "STARTED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return True
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
        self.back_reference.set_state(PlannedActivityArtifactState(self.back_reference))
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state already set to STARTED")
        # do nothing since the artifact is already in the STARTED state

    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))


    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        self.back_reference.set_state(CompletedActivityArtifactState(self.back_reference))
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")


class ContinualActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the CONTINUAL state of an activity artifact"""

    name = "CONTINUAL"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False
    
    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return True
    
    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
        self.back_reference.set_state(PlannedActivityArtifactState(self.back_reference))
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state already set to CONTINUAL")
        # do nothing since the artifact is already in the CONTINUAL state

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        complete_activity(self.back_reference)
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    


class BlockedActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the BLOCKED state of an activity artifact"""
    
    name = "BLOCKED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False

    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return False

    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return True

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
        self.back_reference.set_state(PlannedActivityArtifactState(self.back_reference))
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state already set to BLOCKED")
        # do nothing since the artifact is already in the BLOCKED state
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        complete_activity(self.back_reference)
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")


class CanceledActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the CANCELED state of an activity artifact"""
    
    name = "CANCELED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return True

    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return False

    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
        self.back_reference.set_state(PlannedActivityArtifactState(self.back_reference))
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))


    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state already set to CANCELED")
        # do nothing since the artifact is already in the CANCELED state
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        complete_activity(self.back_reference)
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")


class ReassignedActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the REASSIGNED state of an activity artifact"""

    name = "REASSIGNED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return False

    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return True

    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
        self.back_reference.set_state(PlannedActivityArtifactState(self.back_reference))
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state already set to REASSIGNED")
        # do nothing since the artifact is already in the REASSIGNED state
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state set to COMPLETED")
        complete_activity(self.back_reference)
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")



class CompletedActivityArtifactState(ActivityArtifactState):
    """Concrete class representing the COMPLETED state of an activity artifact"""

    name = "COMPLETED"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        cls.state_registry[cls.name] = cls

    def is_closed(self) -> bool:
        """returns True if the artifact is in a closed state, False otherwise"""
        return True

    def is_in_work(self) -> bool:
        """returns True if the artifact is in a work state, False otherwise"""
        return False

    def is_blocked(self) -> bool:
        """returns True if the artifact is in a blocked state, False otherwise"""
        return False

    def plan(self) -> None:
        """sets the state of the artifact to PLANNED"""
        logging.info("Artifact state set to PLANNED")
    
    def start(self) -> None:
        """sets the state of the artifact to STARTED"""
        logging.info("Artifact state set to STARTED")
        start_activity(self.back_reference)
    
    def continual(self) -> None:
        """sets the state of the artifact to CONTINUAL"""
        logging.info("Artifact state set to CONTINUAL")
        self.back_reference.set_state(ContinualActivityArtifactState(self.back_reference))

    def block(self) -> None:
        """sets the state of the artifact to BLOCKED"""
        logging.info("Artifact state set to BLOCKED")
        self.back_reference.set_state(BlockedActivityArtifactState(self.back_reference))
    
    def cancel(self) -> None:
        """sets the state of the artifact to CANCELED"""
        logging.info("Artifact state set to CANCELED")
        self.back_reference.set_state(CanceledActivityArtifactState(self.back_reference))
    
    def reassign(self) -> None:
        """sets the state of the artifact to REASSIGNED"""
        logging.info("Artifact state set to REASSIGNED")
        self.back_reference.set_state(ReassignedActivityArtifactState(self.back_reference))
    
    def complete(self) -> None:
        """sets the state of the artifact to COMPLETED"""
        logging.info("Artifact state alreadyset to COMPLETED")
        # do nothing since the artifact is already in the COMPLETED state
    
    def activate(self) -> None:
        """sets the state of the artifact to ACTIVE"""
        logging.info("Artifact State not changed, differing state types")
    
    def deactivate(self) -> None:
        """sets the state of the artifact to INACTIVE"""
        logging.info("Artifact State not changed, differing state types")
