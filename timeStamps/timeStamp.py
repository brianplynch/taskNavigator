"""provides time-stamp"""

from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Protocol


class DateComponents(Protocol):
    year: int
    month: int
    day: int


class TimeStamp:
    
    # The COURSE_TIME_INTERVAL is an integer of minutes representing 
    # the interval of time which must be reported
    INTERVAL = 30 # minutes

    DATETIME_FORMAT = "%Y%m%d_%H%M"
    DATE_FORMAT = "%Y%m%d"
    DATE_HOUR_FORMAT = "%Y%m%d_%H"
    INTERVALS_PER_HOUR = 60 // INTERVAL
    
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour

        if self.INTERVAL == 0:
            raise ValueError("course_time_interval has been set to 0 which is not allowed")
        
        if 60 % self.INTERVAL > 0:
            raise ValueError("COURSE_TIME_INTERVAL must be a factor of 60, e.g. 1,2,3,4,5,6,10,12,15,20,30,60")
        
        minute_intervals = [(minute * self.INTERVAL, (minute + 1) * self.INTERVAL) for minute in range(60//self.INTERVAL)]
        self.minute = [a for a,b in minute_intervals if minute>=a and minute<b][0]

    def time_index(self) -> int:
        datetime_stamp = int(self.datetime().timestamp() * 1000)
        return datetime_stamp
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeStamp):
            return False

        is_equal = all(
            [
                self.year == other.year,
                self.month == other.month,
                self.day == other.day,
                self.hour == other.hour,
                self.minute == other.minute
            ]
        )
        return is_equal
    
    def in_date(self, date: DateComponents) -> bool:
        time_stamp_contains_date = all(
            [
                self.year == date.year,
                self.month == date.month,
                self.day == date.day
            ]
        )
        return time_stamp_contains_date
    
    def build(self) -> str:
        """Returns a string representing a date-time object with half-hour precision
        - minutes are 00 if within the first half of the hour
        - minutes are 30 if after the first half of the hour
        # Example
        YYYYMMDD_HH00 or YYYYMMDD_HH30"""

        return f"{self.year}{self.month:02d}{self.day:02d}_{self.hour:02d}{self.minute:02d}"
    
    @classmethod
    def parse(cls, time_stamp_str: str) -> TimeStamp:
        """Returns a TimeStamp object from a string representation of a date-time with half-hour precision
        - minutes are 00 if within the first half of the hour
        - minutes are 30 if after the first half of the hour
        # Example
        YYYYMMDD_HH00 or YYYYMMDD_HH30"""

        dt = datetime.strptime(time_stamp_str, cls.DATETIME_FORMAT)
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    
    @classmethod
    def now(cls) -> TimeStamp:
        """Returns a TimeStamp object representing the current date and time"""
        now = datetime.now()
        return cls(now.year, now.month, now.day, now.hour, now.minute)
    
    def datetime(self) -> datetime:
        """Returns a datetime object representing the date and time of the TimeStamp object"""
        return datetime(self.year, self.month, self.day, self.hour, self.minute)

    @classmethod
    def generate_timestamps(cls, target_date: datetime) -> list[TimeStamp]:
        """returns a list of course timestamps for today (all day)"""
        target_date -= timedelta(hours=target_date.hour, minutes=target_date.minute, seconds=target_date.second)
        start_of_day = cls.from_datetime(target_date + timedelta(hours=0))
        end_of_day = cls.from_datetime(target_date + timedelta(hours=23))
        todays_timestamps = cls.generate_timestamp_range(start_of_day, end_of_day)
        return todays_timestamps

    @classmethod
    def from_datetime(cls, date_time: datetime) -> TimeStamp:
        """Returns a TimeStamp object representing a date-time with half-hour precision
        - minutes are 00 if within the first half of the hour
        - minutes are 30 if after the first half of the hour
        # Example
        YYYYMMDD_HH00 or YYYYMMDD_HH30"""
        return cls(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)

    @classmethod
    def generate_timestamp_range(cls, timestamp_a: TimeStamp, timestamp_b: TimeStamp) -> list[TimeStamp]:
        """returns a list of timestamps between timestamp_a and timestamp_b
        range includes timestamp_a and timestamp_b"""
        if timestamp_a == timestamp_b:
            return [timestamp_a]
        
        timestamp_range: list[str] = list()
        target_time = timestamp_a.datetime()

        while target_time < timestamp_b.datetime():
            timestamp_range.append(cls.from_datetime(target_time))
            target_time += timedelta(minutes=cls.INTERVAL)
        
        if len(timestamp_range) <= 1:
            return [timestamp_a]
        
        if timestamp_range[-1] != timestamp_b:
            timestamp_range.append(timestamp_b)

        return timestamp_range

    def forward_interval(self, intervals: int = 1) -> TimeStamp:
        sign = [-1, 1][intervals >= 0]
        return self.from_datetime(self.datetime() + sign * timedelta(minutes=(abs(intervals) * self.INTERVAL)))
        