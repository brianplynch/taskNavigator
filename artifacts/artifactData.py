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

class ArtifactData:
    """ArtifactData class definition
    """
    builder: ArtifactBuilder
    child_type: ArtifactData

    artifact_type: str
    """defined by sub-classes"""
    
    parent_type: ArtifactData
    """parent_type is set for the child type when the child_type class attribute is set for the parent"""

    artifact_type_registry: dict[str, type[ArtifactData]] = {}
    """The artifact_type_registry maps a string value to a class object"""

    def __init__(self,
        identifier: Identifier,
        detail: str,        #TODO: add in this attribute
        client: Identifier,
        parent: Identifier,
        statement_of_work: str,
        work_breakdown: str,
        work_authorization: Identifier,
        state: ArtifactState, #TODO: confirm whether this should be Type[ArtifactState]
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
        self.detail               = detail
        self.client               = client
        self.parent               = parent
        self.statement_of_work    = statement_of_work
        self.work_breakdown       = work_breakdown
        self.work_authorization   = work_authorization
        self.state                = state(self)
        self.created              = created
        self.started              = started
        self.completed            = completed
        self.resources            = resources
        self.deliverables         = deliverables
        self.plan                 = plan if not plan.is_null else Plan([])
        self.proxy                = proxy
        self.results              = results

