""""""

class ResourceBuilder:
    def build(cls, resource_name: str, line_items: list[tuple[str, str]]) -> str:
        raise NotImplementedError()

    @classmethod
    def parse(cls, resource_type: type, full_resource_str: str):
        raise NotImplementedError()
