"""
"""




from identifiers.identifier import Identifier
from states.artifactState import ArtifactState
from states.noneState import NoneState
from typing import Protocol


class StateProxy(Protocol):
    state_registry: dict

    
class ArtifactProxy(Protocol):
    state: StateProxy
    def load(cls, identifier: Identifier):...


class PlanBuilder:
    """PlanBuilder class definition
    """
    @classmethod
    def build(cls, artifacts: list[ArtifactProxy], state_names: list[str]) -> str:
        raise NotImplementedError("Plan building is not implemented yet")
    
    @classmethod
    def parse(cls, plan_type: type, plan_text: str, artifact_type: type):
        """Parse a plan from text
        """
        raise NotImplementedError("Plan parsing is not implemented yet")