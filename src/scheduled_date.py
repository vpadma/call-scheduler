from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Final

from .resident import Resident


@dataclass
class ScheduledDate:
    date: Final[date]
    is_holiday: Final[bool] = False
    junior_on_call: Resident = field(default=None, init=False)
    senior_on_call: Resident = field(default=None, init=False)

    def is_weekend(self) -> bool:
        return self.date.weekday() >= 5

    # Needed to prevent special cases -- do not schedule on Friday if the resident worked last weekend
    def is_friday(self) -> bool:
        return self.date.weekday() == 4

    def next_weekend(self) -> date:
        return self.date + timedelta(days=self.__get_days_to_next_weekend())

    def previous_weekend(self) -> date:
        return self.date - timedelta(days=self.__get_days_from_previous_weekend())

    def __get_days_from_previous_weekend(self) -> int:
        # Monday long weekend
        if self.date.weekday() == 0 and self.is_holiday:
            return 8
        else:
            return self.date.weekday() + 1

    def __get_days_to_next_weekend(self) -> int:
        if 5 - self.date.weekday() > 0:
            return 5 - self.date.weekday()
        else:
            return 5 - self.date.weekday() + 7

    def set_on_call(self, junior: Resident, senior: Resident) -> None:
        self.junior_on_call = junior
        self.senior_on_call = senior

    def print_on_call(self):
        print(f"Date: {self.date}, Junior: {self.junior_on_call.name}, Senior: {self.senior_on_call.name}")
        
    def to_csv_row(self) -> tuple[date, str, str]:
        return self.date, self.junior_on_call.name, self.senior_on_call.name
