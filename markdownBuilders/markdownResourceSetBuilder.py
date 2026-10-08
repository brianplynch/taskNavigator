""""""


from resources.resource import Resource
from stringList.stringList import FrontLoad


class MarkdownResourceSetBuilder:
    resource_sep: str = "\n### "

    def build(self, resource_set) -> str:
        if not resource_set:
            return ""
        return FrontLoad.join([res.build() for res in resource_set], self.resource_sep)
    
    @classmethod
    def parse(cls, resource_set_type: type, resource_set_str: str):
        if not resource_set_str:
            return resource_set_type([])
        resource_set = [resource_str.strip() for resource_str in FrontLoad.split("\n" + resource_set_str + " ", cls.resource_sep) if resource_str.strip()]
        return resource_set_type([Resource.parse(res_str) for res_str in resource_set])
    
    