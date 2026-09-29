"""

"""

from plans.plan import Plan
from results.resultSet import ResultSet
from states.activeArtifactState import ActiveArtifactState
from artifacts.artifact import Artifact
import logging
from identifiers.identifier import Identifier
from timeStamps.dateStamp import DateStamp

class Process(Artifact):
    """Process class definition
    """
    artifact_type = "Process"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        if cls.artifact_type in Artifact.artifact_type_registry:
            logging.info(f"Artifact type '{cls.artifact_type}' is already registered.")
        Artifact.artifact_type_registry[cls.artifact_type] = cls
    
    def get_all_identifiers(self) -> list[Identifier]:
        all_identifiers = list()
        all_identifiers.extend([artifact.identifier for artifact in self.get_roles()])
        all_identifiers.extend([artifact.identifier for artifact in self.get_responsibilities()])
        all_identifiers.extend([artifact.identifier for artifact in self.get_activities()])
        all_identifiers.extend([artifact.identifier for artifact in self.get_tasks()])
        return all_identifiers

    def get_roles(self):
        roles = self.get_children(0)
        return roles

    def get_responsibilities(self):
        responsibilities = list()
        roles = self.get_roles()
        for role in roles:
            responsibilities.extend(role.get_children(0))
        return responsibilities

    def get_activities(self):
        activities = list()
        responsibilities = self.get_responsibilities()
        for resp in responsibilities:
            activities.extend(resp.get_children(0))
        return activities

    def get_tasks(self):
        tasks = list()
        activities = self.get_activities()
        for act in activities:
            tasks.extend(act.get_children(0))
        return tasks
        

    def new_child(self, title: str) -> None:
        all_identifiers = self.get_all_identifiers()
        identifier = Identifier.new(all_identifiers, title)
        statement_of_work = title
        child = self.child_type(
            identifier = identifier,
            detail = identifier.primary_id,
            client = Identifier.null(),
            parent = self.identifier,
            statement_of_work = statement_of_work,
            work_breakdown = self.work_breakdown,
            work_authorization = self.work_authorization,
            state = ActiveArtifactState,
            created = DateStamp.today(),
            started = DateStamp.null(),
            completed = DateStamp.null(),
            resources = self.resources,
            deliverables = self.deliverables,
            plan = Plan.new_empty(ActiveArtifactState),
            proxy = Identifier.null(),
            results = ResultSet.new_empty(),
            artifact_type = "Process"
        )
        child.save()
        with self as artifact:
            artifact.add_to_plan(child)

    


