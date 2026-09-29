"""

"""

from pathlib import Path
from plans.plan import Plan
from results.resultSet import ResultSet
from states.activityArtifactState import ActivityArtifactState
from artifacts.artifact import Artifact
from identifiers.identifier import Identifier
from timeStamps.dateStamp import DateStamp
from fileio.files import open_file, output_to_file

class Responsibility(Artifact):
    """Responsibility class definition
    """
    artifact_type = "Responsibility"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def new_child(self, title: str) -> None:
        raise NotImplementedError("new_child must be implemented in the subclasses")
    
    def get_all_identifiers(self) -> Identifier:
        """forwards the command to the parent artifact, until it reaches the top level process"""
        return self.get_parent_artifact().get_all_identifiers()
    
    def get_roles(self):
        return self.get_parent_artifact().get_roles()

    def get_responsibilities(self):
        return self.get_parent_artifact().get_responsibilities()

    def get_activities(self):
        return self.get_parent_artifact().get_activities()

    def get_tasks(self):
        return self.get_parent_artifact().get_tasks()

    def get_results(self):
        results = self.results.new_empty()
        for child in self.get_children_artifacts():
            results.merge(child.get_results())
        return results
    
    def get_all_tasks_results(self):
        return self.get_parent_artifact().get_all_tasks_results()
    
    def get_hours(self) -> float:
        total_hours = 0.0
        for child in self.get_children_artifacts():
            total_hours += child.get_hours()
        return total_hours
    
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
            state = ActivityArtifactState,
            created = DateStamp.today(),
            started = DateStamp.null(),
            completed = DateStamp.null(),
            resources = self.resources,
            deliverables = self.deliverables,
            plan = Plan.new_empty(ActivityArtifactState),
            proxy = Identifier.null(),
            results = ResultSet(list()),
            artifact_type = "Activity"
        )
        child.save()
        with self as artifact:
            artifact.add_to_plan(child)

    def open_best_practices_file(self) -> None:
        best_practices_path = Path(self.builder.vault).joinpath(f"{self.identifier.primary_id}_Best_Practices.md")
        if best_practices_path.exists():
            open_file(best_practices_path)
        else:
            subtask_work_instructions = [f"## {task}\n\n![[{task}_WI]]\n\n" for task in self.work_breakdown.splitlines()]
            best_practices_text = f"# {self.identifier.primary_id}_Best_Practices\n\n{chr(10).join(subtask_work_instructions)}"
            with open(best_practices_path, 'a') as bpfile:
                bpfile.write(best_practices_text)
            open_file(best_practices_path)