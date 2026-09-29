"""

### STATENAME

- [[primaryIdent -secondaryident -001]]

"""


import logging
from identifiers.identifier import Identifier
from plans.plan import ArtifactProxy
from states.artifactState import ArtifactState
from states.noneState import NoneState
from stringList.stringList import FrontLoad


STATE_SEP: str = "\n### "

ID_SEP: str = "\n- "


class MarkdownPlanBuilder:
    """MarkdownPlanBuilder class definition
    """
    @classmethod
    def build(cls, artifacts: list[ArtifactProxy], state_names: list[str]) -> str:
        """Build a plan as a markdown string
        """
        plan_markdown_text: str = ""

        for state_name in state_names:
            plan_markdown_text += f"### {state_name}\n\n"
            art_in_state = list(filter(lambda a: a.state.name == state_name, artifacts))
            art_ids = [art.identifier.build_reference() for art in art_in_state]
            plan_markdown_text += FrontLoad.join(art_ids, ID_SEP)
        plan_markdown_text += "\n\n"
        return plan_markdown_text

    @classmethod
    def parse(cls, plan_type: type, plan_text: str, artifact_type: type[ArtifactProxy]):
        """Parse a plan from text
        """
        if not plan_text.startswith(STATE_SEP):
            plan_text = STATE_SEP + plan_text.strip(STATE_SEP)

        artifact_ids = list()
            
        states_artifacts = FrontLoad.split(plan_text, STATE_SEP)

        for state_artifact_str in states_artifacts:
            if "\n" not in state_artifact_str:
                continue
            state_name, artifact_str = state_artifact_str.split("\n", maxsplit=1)
            if not artifact_str.startswith(ID_SEP):
                artifact_str = ID_SEP + artifact_str.strip(ID_SEP)
            artifacts_id_text = FrontLoad.split(artifact_str, ID_SEP)
            artifact_ids.extend([Identifier.parse_reference(artifact_id_str.strip(ID_SEP).strip()) for artifact_id_str in artifacts_id_text])

        children = [artifact_type.load(art_id) for art_id in artifact_ids if not art_id.is_null()]
        return plan_type(children)
