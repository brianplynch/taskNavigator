"""

"""
from __future__ import annotations
from random import randint
from resources.resourceBuilder import ResourceBuilder


class MarkdownResourceBuilder(ResourceBuilder):
    @classmethod
    def build(cls, resource_name: str, line_items: list[tuple[str, str]]) -> str:
        """
        Build a markdown string representation of the resource.
        The markdown format will be:

        ### Resource Name
        line_item_id || line_item_content

        """

        markdown_str = f"{resource_name}\n\n"

        if not line_items:
            return markdown_str
        
        for line_item in line_items:
            if len(line_item) == 2:
                ident, description = line_item
                if ident.startswith("?:"):
                    markdown_str += f"{description}\n"
                else:
                    markdown_str += f"{ident} || {description}\n"
            else:
                markdown_str += f"{str(line_item)}\n"

        return markdown_str

    @classmethod
    def parse(cls, resource_type: type, full_resource_str: str):
        if "\n" not in full_resource_str:
            resource_name = full_resource_str
            return resource_type(resource_name)

        resource_name, line_contents = full_resource_str.split("\n", maxsplit=1)
        resource_name = resource_name.strip()

        line_items = list()
        for line in line_contents.split("\n"):
            if line.strip() == "":
                continue
            if "||" in line:
                line_item_id, line_item_content = line.split("||", maxsplit=1)
                line_items.append((line_item_id.strip(), line_item_content.strip()))
            else:
                # this random_ident doesn't feed into the build method, 
                # it is ignored, but used for the purpose of merging 2 ResourceSet objects
                line_items.append((cls.random_ident(), line))

        return resource_type(resource_name, line_items)

    @staticmethod
    def random_ident() -> str:
        """returns a string with a prefix and a random set of 4 characters
        e.g. "?:s3q9"
        """
        return f"?:{''.join([sorted('1234567890qwertyuiopasdfghjklzxcvbnm')[x] for x in [randint(0,35) for _ in range(4)]])}"