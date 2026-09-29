""""""

class ResourceSetBuilder:
    def build(self, resource_set):
        raise NotImplementedError()
    
    @classmethod
    def parse(cls, resource_set_type: type, resource_set: list):
        raise NotImplementedError()