"""

"""
from __future__ import annotations

from timeStamps.timeStamp import TimeStamp
from identifiers.identifier import Identifier
from results.resultBuilder import ResultBuilder


class ResultData:
    """
    A class to represent a result in an artifact.
    """
    def __init__(self, time_stamp: TimeStamp,    work_authorization: Identifier,    description: str):

        self.time_stamp: TimeStamp = time_stamp
        self.work_authorization: Identifier = work_authorization
        self.description: str = description

    def __repr__(self)-> str:
        """Timestamp | work_auth | descrip (first 9 characters arbitrary)"""
        return f"{self.time_stamp.build()} | {self.work_authorization.build_reference()} | {self.description[:9]}"


class Result(ResultData):
    """
    A class to represent a result in an artifact, inheriting from ResultData.
    """
    
    builder: ResultBuilder

    def __init__(self, time_stamp: TimeStamp,    work_authorization: Identifier,    description: str):
        super().__init__(time_stamp, work_authorization, description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False

        is_equal = all(
            [
                self.time_stamp == other.time_stamp,
                self.work_authorization == other.work_authorization,
                self.description == other.description
            ]
        )
        return is_equal

    
    def __add__(self, other: Result) -> Result:
        if not isinstance(other, Result):
            raise ValueError("Can only add another Result to this Result")

        if self.time_stamp != other.time_stamp:
            raise ValueError("Cannot add Results with different time stamps")

        if self.work_authorization != other.work_authorization:
            raise ValueError("Cannot add Results with different work authorization numbers")

        combined_description = f"{self.description}\n\n{other.description}"
        return Result(self.time_stamp, self.work_authorization, combined_description)
    
    @classmethod
    def log(cls, time_stamp, work_authorization_number: Identifier, description: str = "...") -> Result:
        return cls(time_stamp, work_authorization_number, description)
    
    @classmethod
    def log_now(cls, work_authorization_number: Identifier, description: str = "...") -> Result:
        time_stamp = TimeStamp.now()
        return cls(time_stamp, work_authorization_number, description)
    
    @classmethod
    def log_next(cls, work_authorization_number: Identifier, description: str = "...") -> Result:
        time_stamp = TimeStamp.now().forward_interval(1)
        return cls(time_stamp, work_authorization_number, description)
    
    @classmethod
    def log_previous(cls, work_authorization_number: Identifier, description: str = "...") -> Result:
        time_stamp = TimeStamp.now().forward_interval(-1)
        return cls(time_stamp, work_authorization_number, description)
    
    def prepend_description(self, additional_description: str) -> None:
        self.description = f"{additional_description}\n\n{self.description}"

    def build(self) -> str:
        return self.builder.build(self.time_stamp, self.work_authorization, self.description)
    
    @classmethod
    def parse(cls, full_result_str: str):
        return cls.builder.parse(cls, full_result_str)
    

