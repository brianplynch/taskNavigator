"""

"""


from __future__ import annotations

from identifiers.identifier import Identifier
from timeStamps.timeStamp import TimeStamp


class MarkdownResultBuilder:
    result_attribute_sep: str = "\n> "
    @classmethod
    def build(cls, time_stamp: TimeStamp, work_authorization: Identifier, description: str) -> str:
        """
        Build a markdown string representation of the results.
        The markdown format will be:

        ## Results
        ### time_stamp
        > work_authorization
        > description

        """
        description = description if description else "..."
        result_attributes = [time_stamp.build(), work_authorization.build_reference(), description]

        markdown_str = (cls.result_attribute_sep).join(result_attributes)

        return markdown_str

    @classmethod
    def parse(cls, result_type: type, full_result_str: str):
        parts = full_result_str.split(cls.result_attribute_sep, maxsplit=2)

        time_stamp = TimeStamp.parse(parts[0].strip("# \n"))
        work_authorization = Identifier.parse_reference(parts[1].strip())
        description = parts[2].strip()
        return result_type(time_stamp, work_authorization, description)