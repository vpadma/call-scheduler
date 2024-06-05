from __future__ import annotations

import uuid
from dataclasses import dataclass, InitVar, field
from datetime import date, timedelta
from typing import Final

from .resident import Resident
from .scheduled_date import ScheduledDate


class Schedule:
    residents: Final[dict[uuid.UUID, Resident]]
    start_date: Final[date]
    end_date: Final[date]
    holidays: Final[set[date]]
    dates = dict[date, ScheduledDate]
    total_stats: TotalStats
    monthly_stats: dict[int, MonthStats] = dict()

    def __init__(self, residents: list[Resident], start_date: date, end_date: date, holidays: set[date]) -> None:
        if start_date > end_date:
            raise ValueError("Start date must be before end date")

        self.residents = {resident.id: resident for resident in residents}
        self.start_date = start_date
        self.end_date = end_date
        self.holidays = holidays
        # Create the initial blank schedule
        self.dates = {d: ScheduledDate(d, d in self.holidays) for d in [start_date + timedelta(days=x) for x in
                                                                        range((end_date - start_date).days + 1)]}
        self.total_stats = self.TotalStats(residents)
        # Create the initial monthly stats
        self.monthly_stats = {month: self.MonthStats(month, residents) for month in range(1, 13)}

    def schedule_date(self, date: date, junior: Resident, senior: Resident) -> None:
        self.dates[date].set_on_call(junior, senior)
        self.dates[date].print_on_call()
        self.total_stats.record_residents_on_call(junior, senior)
        self.monthly_stats[date.month].record_residents_on_call(junior, senior)

    def to_csv_format(self) -> list[tuple[date, str, str]]:
        return [date.to_csv_row() for date in self.dates.values()]
        
    def get_junior_residents_load(self) -> dict[uuid.UUID, int]:
        return {resident.id: self.total_stats.resident_load[resident.id] for resident in self.residents.values() if
                resident.is_junior()}

    def get_senior_residents_load(self) -> dict[uuid.UUID, int]:
        return {resident.id: self.total_stats.resident_load[resident.id] for resident in self.residents.values() if
                resident.is_senior()}

    def get_junior_residents_load_for_month(self, month: int) -> dict[uuid.UUID, int]:
        return {resident.id: self.monthly_stats[month].resident_load[resident.id] for resident in
                self.residents.values() if resident.is_junior()}

    def get_senior_residents_load_for_month(self, month: int) -> dict[uuid.UUID, int]:
        return {resident.id: self.monthly_stats[month].resident_load[resident.id] for resident in
                self.residents.values() if resident.is_senior()}

    @dataclass
    class TotalStats:
        residents: InitVar[list[Resident]]
        resident_load: dict[uuid.UUID, int] = field(init=False)

        def __post_init__(self, residents: list[Resident]) -> None:
            self.resident_load = {resident.id: 0 for resident in residents}

        def record_residents_on_call(self, junior: Resident, senior: Resident) -> None:
            self.resident_load[junior.id] += 1
            self.resident_load[senior.id] += 1

    @dataclass
    class MonthStats:
        month: Final[int]
        residents: InitVar[list[Resident]]
        resident_load: dict[uuid.UUID, int] = field(init=False)

        def __post_init__(self, residents: list[Resident]) -> None:
            self.resident_load = {resident.id: 0 for resident in residents}

        def record_residents_on_call(self, junior: Resident, senior: Resident) -> None:
            self.resident_load[junior.id] += 1
            self.resident_load[senior.id] += 1
