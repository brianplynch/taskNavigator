"""

"""

from plans.plan import Plan
from results.resultSet import ResultSet
from states.activityArtifactState import ActivityArtifactState
from artifacts.artifact import Artifact
from identifiers.identifier import Identifier
from fileio.files import open_folder
import logging

from timeStamps.dateStamp import DateStamp


class Activity(Artifact):
    """Activity class definition
    """
    artifact_type = "Activity"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def open_project_folder(self) -> None:
        open_folder(self.builder.vault, self.identifier.build())

    def get_all_tasks_results(self):
        return self.get_parent_artifact().get_all_tasks_results()
    
    def get_proxy_hours(self) -> float:
        """For multiple-level proxy artifact schemes,
            the summarized proxy hours may represent double-dipped
            hours with lower-order proxies, so care should be exercised when creating reports with proxy hours
        """
        total_hours = 0.0
        children = self.get_children_artifacts()
        for child in children:
            total_hours += child.get_proxy_hours()
        return total_hours
    
    def new_child(self, title: str) -> None:
        raise NotImplementedError("new_child must be implemented in the subclasses")
    
    def new_children_from_work_breakdown(self) -> None:
        work_breakdown_items: list[str] = self.work_breakdown.splitlines()
        logging.debug(work_breakdown_items)
        for title in work_breakdown_items:
            self.new_child(title)

    def set_client(self, client: Artifact) -> None:
        if not self.client.is_null():
            if self.client != client.identifier:
                raise RuntimeError(f"activity {self.identifier.build_reference()} already has a client artifact defined")
        
        if not client.proxy.is_null():
            if client.proxy != self.identifier:
                raise RuntimeError(f"task {client.identifier.build_reference()} already has a proxy artifact defined")

        with self as act_art:
            act_art.client = client.identifier

        with client as task_art:
            task_art.proxy = self.identifier

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
    
    def new_child(self, title: str) -> None:
        all_identifiers = self.get_all_identifiers()
        identifier = Identifier.new(all_identifiers, title)
        statement_of_work = title
        work_breakdown = title

        child = self.child_type(
            identifier = identifier,
            detail = identifier.primary_id,
            client = Identifier.null(),
            parent = self.identifier,
            statement_of_work = statement_of_work,
            work_breakdown = work_breakdown,
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
            artifact_type = "Task"
        )
        child.save()
        self.add_to_plan(child)
        logging.debug(f"{str(self.identifier)} plan: " + self.plan.build())
