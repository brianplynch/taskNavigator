""""""

class ResultSetBuilder:
    def build(self, result_set):
        raise NotImplementedError()

    @classmethod
    def parse(cls, result_set_type: type, result_set_str: str):
        raise NotImplementedError()
