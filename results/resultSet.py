""""""

from __future__ import annotations
from results.result import Result
from results.resultSetBuilder import ResultSetBuilder
from timeStamps.timeStamp import TimeStamp
from timeStamps.dateStamp import DateStamp
import logging


class ResultSetData:
    result_set: list[Result]



class ResultSet(ResultSetData):
    
    builder: ResultSetBuilder

    def __init__(self, results: list[Result]):
        self.result_set = results

    def build(self):
        return self.builder.build(self.result_set)

    @classmethod
    def parse(cls, result_set_str: str):
        return cls.builder.parse(cls, result_set_str)

    @classmethod
    def new_empty(cls):
        return cls([])

    def log_now(self, work_authorization_number, description: str) -> None:
        raise NotImplementedError()
    


    def merge(self, other: ResultSet) -> None:
        """
        for each result in other
        if other_result is not in self then add it
        if other_result time_stamp is the same as the self_result time_stamp and other_result work_authorization is the same as the self_result work_authorization then combine them into a single result with the descriptions combined with a newline in between
        if other_result time_stamp is the same as the self_result time_stamp but other_result work_authorization is different than the self_result work_authorization then do nothing (results with different work authorization numbers should be treated as separate results even if they have the same time stamp)
        """

        for result in other.result_set:
            result_with_same_time_stamp = list(filter(lambda r: r.time_stamp == result.time_stamp, self.result_set))
            if not result_with_same_time_stamp:
                self.result_set.append(result)
                continue
            
            res_idx = self.result_set.index(result_with_same_time_stamp[0])
            self.result_set[res_idx].description += f"\n\n{result.description}"
    
    def log(self, time_stamp, work_authorization_number, description: str) -> None:
        new_result = Result.log(time_stamp, work_authorization_number, description)
        result_with_same_time_stamp = list(filter(lambda r: r.time_stamp == new_result.time_stamp, self.result_set))
        if result_with_same_time_stamp:
            res_idx = self.result_set.index(result_with_same_time_stamp[0])
            self.result_set[res_idx].description += f"\n\n{new_result.description}"
            return

        self.result_set.append(new_result)

    def log_previous(self, work_authorization_number, description: str) -> None:
        time_stamp = TimeStamp.now().forward_interval(-1)
        self.log(time_stamp, work_authorization_number, description)

    def log_next(self, work_authorization_number, description: str) -> None:
        time_stamp = TimeStamp.now().forward_interval(1)
        self.log(time_stamp, work_authorization_number, description)
        
    def log_now(self, work_authorization_number, description: str) -> None:
        time_stamp = TimeStamp.now()
        self.log(time_stamp, work_authorization_number, description)

    def most_recent_result(self) -> Result:
        if not self.result_set:
            return None
        sorted_results = sorted(self.result_set, key=lambda r: r.time_stamp.datetime(), reverse=True)
        return sorted_results[0]
    
    def total_hours(self) -> float:
        return len(self.result_set) / TimeStamp.INTERVALS_PER_HOUR

    def filter(self, time_stamp_value: list = None, work_authorization_value: list[str] = None, description_value: list[str] = None):
        if not time_stamp_value and not work_authorization_value and not description_value:
            logging.debug("No filter criteria provided, returning whole list")

        if time_stamp_value:
            lambda_time_stamp = lambda res: any([DateStamp.from_datetime(res.time_stamp).in_date(t_stamp) for t_stamp in time_stamp_value])
        else:
            lambda_time_stamp = lambda res: True

        if work_authorization_value:
            lambda_work_authorization = lambda res: any([res.work_authorization == wa for wa in work_authorization_value])
        else:
            lambda_work_authorization = lambda res: True

        if description_value:
            lambda_description = lambda res: any([res.description in desc for desc in description_value])
        else:
            lambda_description = lambda res: True

        filtered_result_set = self.new_empty()
        filtered_result_set.result_set = list(filter(lambda_time_stamp, filter(lambda_work_authorization, filter(lambda_description, self.result_set))))
        return filtered_result_set

