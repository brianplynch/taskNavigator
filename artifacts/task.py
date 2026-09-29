"""

"""

from pathlib import Path
from fileio.files import open_file
from timeStamps.timeStamp import TimeStamp
from results.resultSet import ResultSet
from artifacts.artifact import Artifact
from fileio.files import open_folder, get_filenames_in_path, output_to_file


class Task(Artifact):
    """Task class definition
    """
    artifact_type = "Task"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def open_project_folder(self) -> None:
        """get the activity id and open the activity folder"""
        open_folder(self.builder.vault, self.load(self.parent).identifier.build())
    
    def send_resources_to_children(self) -> None:
        """Tasks have no children, so there won't be any implementation by subclasses"""

    def send_deliverables_to_children(self) -> None:
        """Tasks have no children, so there won't be any implementation by subclasses"""

    def send_resources_to_parent(self) -> None:
        with self.get_parent_artifact() as parent:
            parent.resources.merge(self.resources)

    def send_deliverables_to_parent(self) -> None:
        with self.get_parent_artifact() as parent:
            parent.deliverables.merge(self.deliverables)

    def get_all_tasks_results(self) -> ResultSet:
        return self.get_parent_artifact().get_all_tasks_results()
    
    def get_proxy_hours(self) -> float:
        if not self.proxy.is_null():
            proxy = self.parent_type.load(self.proxy)
            hours = proxy.get_proxy_hours()
            return hours
        else:
            return self.get_hours()
    
    def set_proxy(self, proxy: Artifact) -> None:
        """set the ident of the provided artifact as this task's proxy and also set the proxy artifact's client as this task's ident"""
        if not self.proxy.is_null():
            if self.proxy != proxy.identifier:
                raise RuntimeError(f"task {self.identifier.build_reference()} already has a proxy artifact defined")
        
        if not proxy.client.is_null():
            if proxy.client != self.identifier:
                raise RuntimeError(f"activity {proxy.identifier.build_reference()} already has a client artifact defined")

        with self as task_art:
            task_art.proxy = proxy.identifier

        with proxy as act_art:
            act_art.client = self.identifier
    
    def lesson_learned(self, description: str) -> None:
        vault_files = get_filenames_in_path(self.builder.vault)
        vault_identifiers = [self.identifier.parse(filename) for filename in vault_files]
        LL_ident = self.identifier.new(vault_identifiers, "Lesson Learned")
        LL_filename = LL_ident.build_path()
        lesson_learned_file_contents = f"""# {LL_filename}\n\n## Task\n\n{self.identifier.build_reference()}\n\n## Description\n\n{description}\n\n## Incorporation\n\n"""
        output_to_file(self.builder.vault, LL_filename, lesson_learned_file_contents)
        with self as art:
            art.resources.new("Lesson Learned", [LL_ident.build_reference()])

    def new_child(self, title: str) -> None:
        raise NotImplementedError("Tasks do not have children, but they may have proxy artifacts")

    def get_all_identifiers(self):
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
    
    def open_work_instruction_file(self) -> None:
        work_instruction_path = Path(self.builder.vault).joinpath(f"{self.identifier.primary_id}_WI.md")
        open_file(work_instruction_path)

    def start(self) -> None:
        """Change the state of the task to STARTED"""
        self.state.start()

    def complete(self) -> None:
        self.state.complete()

    def cancel(self) -> None:
        self.state.cancel()

    def previous_result(self, description: str) -> None:
        with self as artifact:
            artifact.results.log_previous(artifact.work_authorization, description)

    def next_result(self, description: str) -> None:
        with self as artifact:
            artifact.results.log_next(artifact.work_authorization, description)

    def backfill_timestamps(self, description: str) -> None:
        most_recent_timestamp = self.get_all_tasks_results().most_recent_result().time_stamp

        time_stamps = TimeStamp.generate_timestamp_range(most_recent_timestamp.forward_interval(), TimeStamp.now())
        for time_stamp in time_stamps:
            self.results.log(time_stamp, self.work_authorization, description)

    def new_child(self, title: str) -> None:
        raise NotImplementedError("Tasks do not have children, but they may have proxy artifacts")
    