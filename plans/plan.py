"""

"""

from __future__ import annotations

from identifiers.identifier import Identifier
from plans.planBuilder import PlanBuilder
from typing import Protocol
import logging


class StateProxy(Protocol):
    state_registry: dict


class ArtifactProxy(Protocol):
    state: StateProxy
    @classmethod
    def load(cls, identifier: Identifier):...


class Plan:

    builder: PlanBuilder
    
    def __init__(self, artifacts: list[ArtifactProxy]):

        self.artifacts: list[ArtifactProxy] = artifacts

        # a null plan is one that exists as a placeholder and will never have artifacts in it
        #self.is_null: bool = False

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

    def remove(self, artifact_identifier: Identifier) -> None:
        """remove the provided artifact identifier from this plan"""
        for stateType in self.state_artifact_map:
            if artifact_identifier in self.state_artifact_map[stateType]:
                self.state_artifact_map[stateType].remove(artifact_identifier)
                self.state_artifact_map[stateType].append(artifact_identifier.null())

    def add(self, artifact: ArtifactProxy) -> None:
        self.artifacts.append(artifact)



'''
class PlanData:
    """Plan data class definition
    """

    def __init__(self, state_artifact_map: dict[ArtifactState, list[Identifier]] = None):
        self.state_artifact_map: dict[ArtifactState, list[Identifier]] = state_artifact_map
        self.artifact_state_type = None

        # a null plan is one that exists as a placeholder and will never have artifacts in it
        self.is_null: bool = False


class PlanOLD(PlanData):
    """Plan class definition
    """
    builder: PlanBuilder
    
    @classmethod
    def new(cls, state_artifact_map: dict[ArtifactState, list[Identifier]] = None):
        return cls(state_artifact_map)

    @classmethod
    def null_plan(cls):
        n_plan = cls()
        n_plan.null_plan = True
        return n_plan
    
    @classmethod
    def new_empty(cls, artifact_state_type: ArtifactState) -> Plan:
        """new_empty creation method allows creation of a plan prior to the creation of the artifact object
        the backreference required for the ArtifactState part of the state_artifact_map 
        will be defined in the artifact object's init method
        """
        empty_plan = cls()
        empty_plan.artifact_state_type = artifact_state_type
        return empty_plan

    def build(self) -> str:
        """Build the plan as a markdown string
        """
        #artifacts = [Artifact.load(ident) for ident in self.get_artifact_ids()]
        #return self.builder.build_alt(artifacts)

        return self.builder.build(self.state_artifact_map)
    
    @classmethod
    def parse(cls, plan_text: str, artifact_state_type: ArtifactState = None):
        return cls.builder.parse(cls, plan_text, artifact_state_type)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        # sam: state artifact map
        self_sam_keynames = [s.name for s in self.state_artifact_map.keys()]
        other_sam_keynames = [s.name for s in other.state_artifact_map.keys()]
        
        # Keys not the same
        if set(self_sam_keynames).difference(set(other_sam_keynames)):
            logging.debug(f"Difference between\n{self_sam_keynames}\nand\n{other_sam_keynames}")
            return False
        
        # Content within a key's value-set is inconsistent
        for k1,artifact_refs1 in self.state_artifact_map.items():
            for k2,artifact_refs2 in other.state_artifact_map.items():
                if k1.name == k2.name:
                    if not all([art in artifact_refs2 for art in artifact_refs1]):
                        logging.debug(f"{artifact_refs1}\nand\n{artifact_refs2}")
                        return False
        return True
    
    def get_artifact_ids(self):
        """
        returns a flattened list of the artifact identifiers from each valid state"""
        artifact_ids = list()
        for state, ids_in_state in self.state_artifact_map.items():
            for id in ids_in_state:
                # id is never empty for any state, an "empty" state will have a null identifier 
                if not id.is_null():
                    artifact_ids.append(id)
        return artifact_ids

    def remove(self, artifact_identifier: Identifier) -> None:
        """remove the provided artifact identifier from this plan"""
        for stateType in self.state_artifact_map:
            if artifact_identifier in self.state_artifact_map[stateType]:
                self.state_artifact_map[stateType].remove(artifact_identifier)
                self.state_artifact_map[stateType].append(artifact_identifier.null())

    def add(self, artifact_identifier: Identifier, stateType: type) -> None:
        """remove the artifact_identifier from the plan if it already exists,
           then add it back in to the correct state
        """
        logging.debug(f"before adding {str(artifact_identifier)}:  {self.state_artifact_map}")
        self.remove(artifact_identifier)
        if stateType not in self.state_artifact_map:
            self.state_artifact_map.update({stateType: [artifact_identifier]})
        else:
            self.state_artifact_map[stateType].append(artifact_identifier)
        if artifact_identifier.null() in self.state_artifact_map[stateType]:
            self.state_artifact_map[stateType].remove(artifact_identifier.null())

        logging.debug(f"after adding {str(artifact_identifier)}:  {self.state_artifact_map}")
'''