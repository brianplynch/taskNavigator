""""""

from __future__ import annotations
from resources.resource import Resource
from resources.resourceSetBuilder import ResourceSetBuilder


class ResourceSetData:
    def __init__(self, resource_set: list[Resource]):
        self.resource_set = resource_set


class ResourceSet(ResourceSetData):
    
    builder: ResourceSetBuilder

    def build(self) -> str:
        return self.builder.build(self.resource_set)
    
    @classmethod
    def parse(cls, full_resource_str: str):
        return cls.builder.parse(cls, full_resource_str)

    def add(self, resource: Resource) -> None:
        if not resource.line_items or not resource.name:
            return
        
        if self.has_resource_ident(resource.name):
            self.merge(ResourceSet([resource]))
            return
        
        self.resource_set.append(resource)

    def new(self, name: str, line_items: list[tuple[str, str]]) -> None:
        self.add(Resource(name, line_items))

    def merge(self, other: ResourceSet) -> None:
        """
        for each resource in other
        if other_resource name is not in self then add it
        if other_resource line_items are different than self then convert them into a dict object and update from other (line_items without an id use its text as an id)
        if other_resource line_items is the same as the self_resource_line_items then do nothing
        """
        for res in other.resource_set:
            if not self.has_resource_ident(res.name):
                self.resource_set.append(res)
            
            self_resource_with_same_name = list(filter(lambda r: r.name == res.name, self.resource_set))[0]
            res_idx = self.resource_set.index(self_resource_with_same_name)
            if res.line_items != self_resource_with_same_name.line_items:
                self_line_items_dict = dict(self_resource_with_same_name.line_items)
                self_line_items_dict.update(dict(res.line_items))
                self.resource_set[res_idx].line_items = list(self_line_items_dict.items())

    def has_resource_ident(self, resource_name: str) -> bool:
        return len(list(filter(lambda r: r.name == resource_name, self.resource_set))) > 0

    def show_names(self) -> list[str]:
        names = [res.name for res in self.resource_set]
        return names

