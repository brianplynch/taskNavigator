"""Artifact class definition
"""

from __future__ import annotations

from results.resultSet import ResultSet
from artifacts.artifactData import ArtifactData
from identifiers.identifier import Identifier
from fileio.files import open_file
from pathlib import Path
import logging


class Artifact(ArtifactData):
    """Artifact class definition
    """
    _edit_mode: bool = False
    
    @classmethod
    def __new__(cls, *args, **kwargs) -> Artifact:
        """Using parent class, create a new instance of a subclass
        """
        # if the subclass is being initialized (i.e. called from super()) then initialize
        if cls.artifact_type:
            return super().__new__(cls)

        #TODO: the below lines force creation to use KWARGS instead of positional ARGS
        if "artifact_type" not in kwargs:
            raise ValueError("artifact_type is required")
        
        if not Artifact.artifact_type_registry:
            raise ValueError("artifact_type_registry is not defined")
        
        artifact_type = kwargs.pop("artifact_type")
        return super().__new__(Artifact.artifact_type_registry[artifact_type])
    


    def __enter__(self):
        """Use a context manager when updating an Artifact so that manual updates are synchronyzed with automated updates"""
        logging.debug(f"Entering Context Manager for {self.identifier.build()}")
        if self._edit_mode:
            # if the artifact is already in _edit_mode from another function (cannot be "locked" by manual editing), save the artifact first then proceed as usual
            self.save()
        self.reload()
        self._edit_mode = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Use a context manager when updating an Artifact so that manual updates are synchronyzed with automated updates"""
        self.save()
        # Ensure that the _edit_mode is released
        self._edit_mode = False
        if exc_type:
            print(f"An error occurred: {exc_val}")
            # Ensure that the _edit_mode is released
            self._edit_mode = False
        
        logging.debug(f"Exiting the Context Manager for {self.identifier.build()}")
        return True
    
    def __str__(self) -> str:
        return self.identifier.build()

    def __repr__(self) -> str:
        return self.identifier.build()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the class immediately upon definition
        if cls.artifact_type in Artifact.artifact_type_registry:
            logging.info(f"Artifact type '{cls.artifact_type}' is already registered.")
        Artifact.artifact_type_registry[cls.artifact_type] = cls

    def build(self) -> str:
        """Build the artifact by calling the build method of the builder
        """
        return self.builder.build(self)

    @classmethod
    def parse(cls, artifact_markdown_str: str):
        """Parse a markdown string to create an Artifact instance
        """
        return cls.builder.parse(cls, artifact_markdown_str)
    
    def save(self) -> None:
        logging.debug(f"saving {str(self.identifier)}")
        self.builder.save(self)

    @classmethod
    def load(cls, identifier: Identifier):
        return cls.builder.load(cls, identifier)
    
    def reload(self) -> None:
        """load the saved data of this artifact from storage and set all attributes to the stored data"""
        logging.debug(f"reloading {str(self.identifier)}")
        loaded_artifact = self.load(self.identifier)
        self.__dict__.update(loaded_artifact.__dict__)
    
    @classmethod
    def set_vault(cls, vault: str) -> None:
        cls.builder.set_vault(vault)

    @classmethod
    def set_parent_type(cls, parent_type) -> None:
        cls.parent_type = parent_type

    @classmethod
    def set_child_type(cls, child_type: Artifact) -> None:
        cls.child_type = child_type
        child_type.set_parent_type(cls)

    def new_child(self) -> None:
        raise NotImplementedError("new_child must be implemented in the subclasses")

    def set_proxy(self, proxy_artifact: Artifact) -> None:
        raise NotImplementedError("new_child must be implemented in the subclasses")

    def set_client(self, client_artifact: Artifact) -> None:
        raise NotImplementedError("new_child must be implemented in the subclasses")

    def get_children(self, max_recurssion: int = 0):
        """
        return list of children objects, 
        following the hierarchy for as many generations as defined by the max_recurssion"""
        children_ids = self.plan.get_artifact_ids()
        children = [self.child_type.load(i) for i in children_ids]

        if max_recurssion == 0:
            return children
        
        for child_id in children_ids:
            child = self.child_type.load(child_id)
            _children_of_child = child.get_children(max_recurssion-1)
            children.extend(_children_of_child)

        return children

    def open_source_file(self) -> None:
        open_file(Path(self.builder.vault).joinpath(self.identifier.build_path()))

    def add_to_plan(self, child_artifact: Artifact):
        with self as artifact:
            artifact.plan.add(child_artifact.identifier, type(child_artifact.state))

    def get_parent_artifact(self) -> Artifact:
        return self.parent_type.load(self.parent)
    
    def new_result(self, description: str) -> None:
        """
        If the artifact is not in work, set the state to an in work state
        If the arftifact is closed, log a new result without changing the state
        """
        with self as artifact:
            if not artifact.state.is_in_work() and not artifact.state.is_closed():
                artifact.start()

        with self as artifact:
            artifact.results.log_now(artifact.work_authorization, description)

    def set_state(self, state) -> None:
        """
        Set the new state
        Log a result
        Update the parent plan
        """
        with self as artifact:
            artifact.state = state

        with self as artifact:
            artifact.new_result("Transition to " + state.name)
        
        with self.get_parent_artifact() as parent:
            parent.add_to_plan(self)

        with self.get_parent_artifact() as parent:
            if not parent.state.is_in_work() and not parent.state.is_closed():
                parent.start()

    def get_proxy_artifact(self) -> list[Artifact]:
        return self.load(self.proxy)
    
    def get_client_artifact(self) -> list[Artifact]:
        return self.load(self.client)

    def get_children_artifacts(self) -> list[Artifact]:
        return self.get_children(max_recurssion=0)
    
    def get_in_work_children(self) -> list[Artifact]:
        children = self.get_children_artifacts()
        return [child for child in children if child.state.is_in_work()]
    
    def get_not_closed_children(self) -> list[Artifact]:
        children = self.get_children_artifacts()
        return [child for child in children if not child.state.is_closed()]

    def send_work_authorization_to_open_children(self) -> None:
        children = self.get_children_artifacts()
        for child in children:
            if not child.state.is_closed() and child.work_authorization != self.work_authorization:
                with child as art:
                    art.work_authorization = self.work_authorization

    def get_rolled_up_results(self) -> ResultSet:
        merged_results = self.results.new_empty()
        children = self.get_children(max_recurssion=4)
        for child in children:
            merged_results.merge(child.get_identified_results())
        return merged_results

    def get_results(self) -> ResultSet:
        results = self.results.new_empty()

        children = self.get_children_artifacts()

        if not children:
            return self.results
        
        for child in children:
            results.merge(child.get_results())
        return results

    def get_identified_results(self) -> ResultSet:
        results = self.results.new_empty()
        
        for result in self.results.result_set:
            result.prepend_description(self.identifier.build_reference())
            results.result_set.append(result)
        return results
    
    def get_all_identifiers(self) -> Identifier:
        raise NotImplementedError("Implemented by subclasses")
    
    def get_roles(self):
        raise NotImplementedError("Implemented by subclasses")

    def get_responsibilities(self):
        raise NotImplementedError("Implemented by subclasses")

    def get_activities(self):
        raise NotImplementedError("Implemented by subclasses")

    def get_tasks(self):
        raise NotImplementedError("Implemented by subclasses")

    def get_hours(self) -> float:
        total_hours = 0.0

        children = self.get_children_artifacts()

        if not children:
            return self.results.total_hours()
        
        for child in children:
            total_hours += child.get_hours()
        return total_hours

    def add_deliverable(self, resource) -> None:
        with self as art:
            art.deliverables.add(resource)

    def add_resource(self, resource) -> None:
        with self as art:
            art.deliverables.add(resource)
            