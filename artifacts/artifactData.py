"""artifactData.py: ArtifactData class definition
"""

from __future__ import annotations
from artifacts.artifactBuilder import ArtifactBuilder
from identifiers.identifier import Identifier
from timeStamps.dateStamp import DateStamp
from states.artifactState import ArtifactState
from resources.resourceSet import ResourceSet
from plans.plan import Plan
from results.resultSet import ResultSet
from dataclasses import dataclass




class ArtifactData:
    """ArtifactData class definition
    """
    builder: ArtifactBuilder
    """manually set"""

    child_type: type[ArtifactData]
    """manually set"""

    state_type: type[ArtifactState]
    """manually set"""

    artifact_type: str
    """defined by sub-classes"""
    
    parent_type: type[ArtifactData]
    """parent_type is set for the child type when the child_type class attribute is set for the parent"""

    artifact_type_registry: dict[str, type[ArtifactData]] = {}
    """The artifact_type_registry maps a string value to a class object"""

    def __init__(self,
        identifier: Identifier,
        client: Identifier,
        parent: Identifier,
        statement_of_work: Descriptive,
        work_breakdown: Descriptive,
        detail: Descriptive,
        work_authorization: Identifier,
        state: ArtifactState,
        created: DateStamp,
        started: DateStamp,
        completed: DateStamp,
        resources: ResourceSet,
        deliverables: ResourceSet,
        plan: Plan,
        proxy: Identifier,
        results: ResultSet,
        artifact_type: str
    ):

        self.identifier           = identifier
        self.client               = client
        self.parent               = parent
        self.statement_of_work    = statement_of_work
        self.work_breakdown       = work_breakdown
        self.detail               = detail
        self.work_authorization   = work_authorization
        self.state                = state(self)
        self.created              = created
        self.started              = started
        self.completed            = completed
        self.resources            = resources
        self.deliverables         = deliverables
        self.plan                 = plan
        self.proxy                = proxy
        self.results              = results

"""
below is under development
"""

@dataclass
class ArtifactIdentifyingData:
    identifier: Identifier
    artifact_type: Descriptive


@dataclass
class ArtifactNEW:
    identifier_data: ArtifactIdentifyingData
    artifact_data: ArtifactData


class Descriptive(str):
    def build(self) -> str:
        return self.__str__()
    
    @classmethod
    def parse(cls, text: str) -> Descriptive:
        descriptive_text: str = text
        if not isinstance(text, str):
            descriptive_text = text.__repr__()

        return Descriptive(descriptive_text)