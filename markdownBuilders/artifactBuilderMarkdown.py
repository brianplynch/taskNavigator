"""
Artifact Markdown Builder
"""

from pathlib import Path
from plans.plan import Plan
from resources.resource import Resource
from resources.resourceSet import ResourceSet
from results.result import Result
from results.resultSet import ResultSet
from artifacts.artifact import Artifact
from artifacts.artifactBuilder import ArtifactBuilder
from identifiers.identifier import Identifier
from markdownBuilders.markdownIdentifierBuilder import MarkdownIdentifierBuilder
from markdownBuilders.markdownPlanBuilder import MarkdownPlanBuilder
from markdownBuilders.markdownResourceBuilder import MarkdownResourceBuilder
from markdownBuilders.markdownResourceSetBuilder import MarkdownResourceSetBuilder
from markdownBuilders.markdownResultBuilder import MarkdownResultBuilder
from markdownBuilders.markdownResultSetBuilder import MarkdownResultSetBuilder
from timeStamps.dateStamp import DateStamp


from states.activityArtifactState import ActivityArtifactState


class ArtifactBuilderMarkdown(ArtifactBuilder):
    """Artifact Markdown Builder: A tool for building markdown representations of artifacts.
    """

    vault: Path = ""

    def __init__(self, vault: str):
        self.set_vault(vault)
        # initialize the independent classes
        Identifier.builder = MarkdownIdentifierBuilder()
        Resource.builder = MarkdownResourceBuilder()
        ResourceSet.builder = MarkdownResourceSetBuilder()
        Result.builder = MarkdownResultBuilder()
        ResultSet.builder = MarkdownResultSetBuilder()
        Plan.builder = MarkdownPlanBuilder()

    @classmethod
    def build(cls, artifact: Artifact) -> str:
        """Render an artifact as markdown
        """

        display_order = [
            ("Artifact Type", artifact.artifact_type),
            ("Client", artifact.client.build_reference()),
            ("Parent", artifact.parent.build_reference()),
            ("Statement of Work", artifact.statement_of_work),
            ("Work Breakdown", artifact.work_breakdown),
            ("Work Authorization", artifact.work_authorization.build_reference()),
            ("State", artifact.state.name),
            ("Created", artifact.created.build()),
            ("Started", artifact.started.build()),
            ("Completed", artifact.completed.build()),
            ("Resources", artifact.resources.build()),
            ("Deliverables", artifact.deliverables.build()),
            ("Plan", artifact.plan.build()),
            ("Proxy", artifact.proxy.build_reference()),
            ("Results", artifact.results.build()),
        ]

        return f"# {artifact.identifier.build()}\n\n" + "\n\n".join(f"## {field_name}\n\n{field_value}" for field_name, field_value in display_order)

    @classmethod
    def parse(cls, artifact_class: type, artifact_markdown_str: str) -> Artifact:
        """Parse a markdown string to create an Artifact instance
        """
        attributes_name_textvalue = artifact_markdown_str.strip("# ").split("\n## ")
        identifier = attributes_name_textvalue[0].strip()
        attributes = {name: textvalue for name, textvalue in map(lambda s: s.split("\n", maxsplit=1), attributes_name_textvalue[1:])}
        state_type = ActivityArtifactState.super_state_registry[attributes["State"].strip()]
        parsed_attributes = {
            "identifier": Identifier.parse(identifier),
            "detail": Identifier.parse(identifier).primary_id,
            "artifact_type": artifact_class.artifact_type,
            "client": Identifier.parse_reference(attributes["Client"].strip()),
            "parent": Identifier.parse_reference(attributes["Parent"].strip()),
            "statement_of_work": attributes["Statement of Work"].strip(),
            "work_breakdown": attributes["Work Breakdown"].strip(),
            "work_authorization": Identifier.parse_reference(attributes["Work Authorization"].strip()),
            "state": state_type,
            "created": DateStamp.parse(attributes["Created"].strip()),
            "started": DateStamp.parse(attributes["Started"].strip()),
            "completed": DateStamp.parse(attributes["Completed"].strip()),
            "resources": ResourceSet.parse(attributes["Resources"].strip()),
            "deliverables": ResourceSet.parse(attributes["Deliverables"].strip()),
            "plan": Plan.parse(attributes["Plan"], artifact_class.child_type) if hasattr(artifact_class, "child_type") else Plan([]),
            "proxy": Identifier.parse_reference(attributes["Proxy"].strip()),
            "results": ResultSet.parse(attributes["Results"].strip())
        }
        return artifact_class(**parsed_attributes)

    def save(self, artifact: Artifact) -> None:
        rendered_markdown = self.build(artifact)
        file_path = Path(self.vault).joinpath(artifact.identifier.build_path())
        
        # Ensure the file exists before writing to it
        if not file_path.exists():
            open(file_path, "a").close()

        with open(file_path, "w") as f:
            f.write(rendered_markdown)

    @classmethod
    def load(cls, artifact_type: Artifact, identifier: Identifier):
        vault_file_path = Path(cls.vault).joinpath(identifier.build_path())
        
        if not vault_file_path.exists():
            raise FileNotFoundError(f"File does not exist:\n{vault_file_path}")
        
        with open(vault_file_path, 'r') as artifact_file:
            artifact_text = artifact_file.read()
        
        return artifact_type.parse(artifact_text)