"""

"""

from __future__ import annotations

from identifiers.identifier import Identifier
from plans.planBuilder import PlanBuilder
from typing import Protocol
import logging


class StateProxy(Protocol):
    state_registry: dict
    name: str


class ArtifactProxy(Protocol):
    state: StateProxy
    identifier: Identifier
    @classmethod
    def load(cls, identifier: Identifier):...


class Plan:

    builder: PlanBuilder
    
    def __init__(self, artifacts: list[ArtifactProxy]):

        self.artifacts: list[ArtifactProxy] = artifacts

    @property
    def is_null(self) -> bool:
        return len([artifact for artifact in self.artifacts if artifact]) == 0

    @property
    def state_names(self) -> list[str]:
        if not self.artifacts:
            return ["NONE"]
        return list(self.artifacts[0].state.state_registry.keys())
    
    def build(self) -> str:
        """Build the plan as a markdown string
        """

        return self.builder.build(self.artifacts, self.state_names)
    
    @classmethod
    def parse(cls, plan_text: str, artifact_type: type[ArtifactProxy]):
        return cls.builder.parse(cls, plan_text, artifact_type)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Plan):
            return False
        return self.artifacts == other.artifacts
        
    def get_artifact_ids(self):
        return [art.identifier for art in self.artifacts]

    def add(self, artifact: ArtifactProxy) -> None:
        if artifact not in self.artifacts:
            self.artifacts.append(artifact)
