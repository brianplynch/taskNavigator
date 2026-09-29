"""

"""

from plans.plan import Plan
from results.resultSet import ResultSet
from states.activeArtifactState import ActiveInactiveArtifactState
from artifacts.artifact import Artifact
from identifiers.identifier import Identifier
from timeStamps.dateStamp import DateStamp


class Role(Artifact):
    """Role class definition
    """
    artifact_type = "Role"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_all_identifiers(self) -> Identifier:
        """forwards the command to the parent artifact, until it reaches the top level process"""
        return self.get_parent_artifact().get_all_identifiers()
    
    def get_all_tasks_results(self):
        return self.get_parent_artifact().get_all_tasks_results()

    def get_results(self) -> ResultSet:
        results = self.results.new_empty()
        for child in self.get_children_artifacts():
            results.merge(child.get_results())
        return results
    
    def get_roles(self):
        return self.get_parent_artifact().get_roles()

    def get_responsibilities(self):
        return self.get_parent_artifact().get_responsibilities()

    def get_activities(self):
        return self.get_parent_artifact().get_activities()

    def get_tasks(self):
        return self.get_parent_artifact().get_tasks()

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
            state = ActiveInactiveArtifactState,
            created = DateStamp.today(),
            started = DateStamp.null(),
            completed = DateStamp.null(),
            resources = self.resources,
            deliverables = self.deliverables,
            plan = Plan.new_empty(ActiveInactiveArtifactState),
            proxy = Identifier.null(),
            results = ResultSet(list()),
            artifact_type = "Responsibility"
        )
        child.save()
        with self as artifact:
            artifact.add_to_plan(child)