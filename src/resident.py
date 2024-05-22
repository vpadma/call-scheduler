from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Final


class ResidentYear(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5


@dataclass(frozen=True)
class Resident:
    id: Final[uuid.UUID]
    name: Final[str]
    year: Final[ResidentYear]
    vacation_days: Final[list[date]]

    def is_senior(self) -> bool:
        return self.year == ResidentYear.FIFTH or self.year == ResidentYear.FOURTH

    def is_senior_for_date(self, date: date) -> bool:
        if date.month in range(2, 7):
            return self.year == ResidentYear.THIRD or self.year == ResidentYear.FOURTH
        else:
            return self.is_senior()

    def is_junior(self) -> bool:
        return not self.is_senior()

    @staticmethod
    def from_yaml(data: dict) -> Resident:
        return Resident(uuid.uuid4(), data["name"], ResidentYear(data["year"]), data["vacation_days"])
