"""provides date-stamp"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Protocol


class DateComponents(Protocol):
    year: int
    month: int
    day: int



class DateStamp:
    """A class representing a date stamp, which is a string representation of a date with the format YYYYMMDD"""
    def __init__(self, year: int, month: int, day: int):
        if year == 0 and month == 0 and day == 0:
            # don't evaluate the below validity checks
            pass
        elif year < 2000:
            raise ValueError("year must be greater than or equal to 2000")
        elif month < 1 or month > 12:
            raise ValueError("month must be between 1 and 12")
        elif day < 1 or day > 31:
            raise ValueError("day must be between 1 and 31")
        else:
            pass

        self.year = year
        self.month = month
        self.day = day

    def day_index(self) -> int:
        datetime_stamp = int(self.datetime().timestamp() * 1000)
        return datetime_stamp

    def __eq__(self, other: object):
        if not isinstance(other, DateStamp):
            return False

        if self.year != other.year:
            return False

        if self.month != other.month:
            return False

        if self.day != other.day:
            return False

        return True

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, DateStamp):
            raise ValueError()

        return self.day_index() < other.day_index()

        """    def __lte__(self, other: object) -> bool:
                if not isinstance(other, DateStamp):
                    raise ValueError()

                return self.day_index() <= other.day_index()

            def __gt__(self, other: object) -> bool:
                if not isinstance(other, DateStamp):
                    raise ValueError()

                return self.day_index() > other.day_index()

            def __gte__(self, other: object) -> bool:
                if not isinstance(other, DateStamp):
                    raise ValueError()

                return self.day_index() >= other.day_index()"""


    def in_date(self, date: DateComponents) -> bool:
        time_stamp_contains_date = all(
            [
                self.year == date.year,
                self.month == date.month,
                self.day == date.day
            ]
        )
        return time_stamp_contains_date

    @classmethod
    def null(cls) -> DateStamp:
        return cls(0,0,0)

    def is_null(self) -> bool:
        return self.year == 0 and self.month == 0 and self.day == 0

    def build(self) -> str:
        """returns a string representation of the date with the format YYYYMMDD"""
        if self.is_null():
            return ""
        
        return f"{self.year:04}{self.month:02}{self.day:02}"
    
    @classmethod
    def parse(cls, date_stamp: str) -> DateStamp:
        """returns a DateStamp object from a string representation of a date with the format YYYYMMDD"""
        if date_stamp == "":
            return cls(0,0,0)
        
        if len(date_stamp) != 8:
            raise ValueError("date_stamp must be in the format YYYYMMDD")
        year = int(date_stamp[0:4])
        month = int(date_stamp[4:6])
        day = int(date_stamp[6:8])
        return cls(year, month, day)
    
    @classmethod
    def from_datetime(cls, date_time: datetime) -> DateStamp:
        """returns a string representation of a datetime object with the format YYYYMMDD"""
        return cls(date_time.year, date_time.month, date_time.day)

    
    def datetime(self) -> datetime:
        """returns a datetime object representing the date stamp"""
        return datetime(self.year, self.month, self.day)
    
    @classmethod
    def today(cls) -> DateStamp:
        """returns a string representation of today's date with the format YYYYMMDD"""
        return cls.from_datetime(datetime.now())
    
    @classmethod
    def week_of_stamps(cls, date_time: datetime) -> list[str]:
        """returns a list of date_stamp strings for a date_time that represent the days of the current workweek"""
        last_day_of_this_week = date_time + timedelta(days=6 - date_time.weekday())
        stamps = [cls.from_datetime(last_day_of_this_week - timedelta(days=i)) for i in range(7)]
        return stamps

    @classmethod
    def this_week_stamps(cls) -> list[str]:
        """returns a list of date_stamp strings for this week"""
        return cls.week_of_stamps(datetime.now())

    @classmethod
    def last_week_stamps(cls) -> list[str]:
        """returns a list of date_stamp strings for last week"""
        return cls.week_of_stamps(datetime.now() - timedelta(days=7))

