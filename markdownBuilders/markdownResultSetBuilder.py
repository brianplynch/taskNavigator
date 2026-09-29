""""""

from results.result import Result
from stringList.stringList import FrontLoad

class MarkdownResultSetBuilder:
    result_sep: str = "\n### "

    def build(self, result_set) -> str:
        return FrontLoad.join([res.build() for res in sorted(result_set, key=lambda r: r.time_stamp.datetime())], self.result_sep)

    @classmethod
    def parse(cls, result_set_type: type, result_set_str: str):
        # if the result set string is empty then return an empty resultset
        if not result_set_str:
            return result_set_type(list())
        result_set = FrontLoad.split(result_set_str, cls.result_sep)
        return result_set_type([Result.parse(res_str) for res_str in result_set])
    
    