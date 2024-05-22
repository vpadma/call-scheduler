from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta
from typing import Callable

import yaml

from src import Resident, ResidentYear, Schedule

RESIDENTS_DIRECTORY = "residents"
RESIDENT_TEMPLATE_FILENAME = "template.yaml"
HOSPITAL_INFO_FILENAME = "hospital_information.yaml"
CSV_OUTPUT_FILENAME = "call_schedule.csv"
MONTHLY_CALL_MAX = 9


class CallScheduler:
    schedule: Schedule
    common_conditions: list[Callable[[date, Resident], bool]] = list()

    def __init__(self, start_date: date, end_date: date) -> None:
        self.schedule = Schedule(CallScheduler.parse_residents(), start_date, end_date,
                                 set(CallScheduler.parse_hospital_information()["holidays"]))
        # Common rules for all residents, junior and senior
        self.common_conditions = [self.is_resident_not_on_vacation,
                                  self.if_weekend_is_resident_already_on_call,
                                  self.if_weekday_is_resident_not_post_call,
                                  self.if_weekend_not_consecutive_weekend,
                                  self.resident_has_enough_call_capacity]

    @staticmethod
    def parse_residents() -> list[Resident]:
        residents = list()
        for filename in os.listdir(RESIDENTS_DIRECTORY):
            if filename == RESIDENT_TEMPLATE_FILENAME:
                continue
            else:
                with open(f"{RESIDENTS_DIRECTORY}/{filename}", "r") as file:
                    try:
                        residents.append(Resident.from_yaml(yaml.safe_load(file)))
                    except yaml.YAMLError as exc:
                        print(exc)
        return residents

    @staticmethod
    def parse_hospital_information() -> dict:
        with open(HOSPITAL_INFO_FILENAME, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)

    def create_schedule(self) -> None:
        for date in self.schedule.dates:
            selected_junior, selected_senior = self.select_optimal_residents_for_date(
                self.get_eligible_juniors_for_date(date), self.get_eligible_seniors_for_date(date), date)
            self.schedule.schedule_date(date, selected_junior, selected_senior)

    def to_csv(self) -> None:
        with open(CSV_OUTPUT_FILENAME, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Junior Resident", "Senior Resident"])
            writer.writerows(self.schedule.to_csv_format())

    # For every date, retrieve the list of eligible residents based on the rules provided. Then sort the list based
    # on what residents have worked the least in the month, and then in total. If there are still ties, pick randomly
    # from the tied residents
    def select_optimal_residents_for_date(self, juniors: list[Resident], seniors: list[Resident], date: date) -> tuple[
        Resident, Resident]:
        if len(juniors) == 0 or len(seniors) == 0:
            print(f"No residents available for selection {date}")
            raise ValueError("No residents available for selection")

        # When fifth years exit the rotation, prioritize filling the senior slot first
        if len(seniors) == 1:
            selected_senior = seniors[0]
            selected_junior = random.choice(self.get_least_monthly_loaded_residents_from_list(
                self.get_least_total_loaded_residents_from_list(
                    list(filter(lambda junior: junior.id != selected_senior.id, juniors))), date.month))
        else:
            selected_junior = random.choice(self.get_least_monthly_loaded_residents_from_list(
                self.get_least_total_loaded_residents_from_list(juniors), date.month))
            selected_senior = random.choice(self.get_least_monthly_loaded_residents_from_list(
                self.get_least_total_loaded_residents_from_list(
                    list(filter(lambda senior: senior.id != selected_junior.id, seniors))), date.month))
        return selected_junior, selected_senior

    def get_least_total_loaded_residents_from_list(self, residents: list[Resident]) -> list[Resident]:
        resident_subset = {id: self.schedule.total_stats.resident_load[id] for id in
                           [resident.id for resident in residents]}
        return [self.schedule.residents[resident_id] for resident_id, load in
                resident_subset.items() if load == min(resident_subset.values())]

    def get_least_monthly_loaded_residents_from_list(self, residents: list[Resident], month: int) -> list[Resident]:
        resident_subset = {id: self.schedule.monthly_stats[month].resident_load[id] for id in
                           [resident.id for resident in residents]}
        return [self.schedule.residents[resident_id] for resident_id, load in
                resident_subset.items() if load == min(resident_subset.values())]

    def get_eligible_juniors_for_date(self, date: date) -> list[Resident]:
        eligible_residents = [resident for resident in self.schedule.residents.values() if resident.is_junior()]
        all_conditions = self.common_conditions + [self.second_year_not_on_call_during_weekends_first_month]
        for condition in all_conditions:
            eligible_residents = list(filter(lambda res: condition(date, res), eligible_residents))
        return eligible_residents

    def get_eligible_seniors_for_date(self, date: date) -> list[Resident]:
        eligible_residents = [resident for resident in self.schedule.residents.values() if
                              resident.is_senior_for_date(date)]
        all_conditions = self.common_conditions + [self.fifth_years_not_on_call_second_half]
        for condition in all_conditions:
            eligible_residents = list(filter(lambda res: condition(date, res), eligible_residents))
        return eligible_residents

    def get_consecutive_days(self, date: date) -> int:
        consecutive_days = 1
        while True:
            if ((date + timedelta(consecutive_days) in self.schedule.dates) and
                    (self.schedule.dates[date + timedelta(consecutive_days)].is_weekend() or
                     self.schedule.dates[date + timedelta(consecutive_days)].is_holiday)):
                consecutive_days += 1
            else:
                break
        return consecutive_days

    # Mark all the call-rules here.
    # If resident is on vacation, they are not eligible. Also check into the future for vacation days
    def is_resident_not_on_vacation(self, date: date, resident: Resident) -> bool:
        return all([day not in resident.vacation_days for day in
                    [date + timedelta(i) for i in range(self.get_consecutive_days(date))]])

    # Weekends and long weekends are consecutive call days (except Easter, which is not covered by this program)
    def if_weekend_is_resident_already_on_call(self, date: date, resident: Resident) -> bool:
        if self.schedule.dates[date].is_weekend() or self.schedule.dates[date].is_holiday:
            previous_date = date - timedelta(1)
            if previous_date not in self.schedule.dates:
                return True
            else:
                return self.schedule.dates[previous_date].junior_on_call.id == resident.id or self.schedule.dates[
                    previous_date].senior_on_call.id == resident.id
        else:
            return True

    # Weekdays are not consecutive call days (also handles case for first day post weekend)
    def if_weekday_is_resident_not_post_call(self, date: date, resident: Resident) -> bool:
        if not self.schedule.dates[date].is_weekend() and not self.schedule.dates[date].is_holiday:
            previous_date = date - timedelta(1)
            if previous_date not in self.schedule.dates:
                return True
            else:
                return self.schedule.dates[previous_date].junior_on_call.id != resident.id and self.schedule.dates[
                    previous_date].senior_on_call.id != resident.id
        else:
            return True

    # Residents cannot work consecutive weekends
    def if_weekend_not_consecutive_weekend(self, date: date, resident: Resident) -> bool:
        if (self.schedule.dates[date].is_weekend() or self.schedule.dates[date].is_holiday or
                self.schedule.dates[date].is_friday()):
            previous_weekend = self.schedule.dates[date].previous_weekend()
            if previous_weekend not in self.schedule.dates:
                return True
            else:
                return self.schedule.dates[previous_weekend].junior_on_call.id != resident.id and self.schedule.dates[
                    previous_weekend].senior_on_call.id != resident.id
        else:
            return True

    # Residents cannot work more than MONTHLY_CALL_MAX days per month
    def resident_has_enough_call_capacity(self, date: date, resident: Resident) -> bool:
        return (self.schedule.monthly_stats[date.month].resident_load[resident.id] +
                self.get_consecutive_days(date) <= MONTHLY_CALL_MAX)

    def second_year_not_on_call_during_weekends_first_month(self, date: date, resident: Resident) -> bool:
        return not (resident.year == ResidentYear.SECOND and self.get_consecutive_days(date) > 1 and date.month == 7)

    def fifth_years_not_on_call_second_half(self, date: date, resident: Resident) -> bool:
        if resident.year == ResidentYear.FIFTH:
            return all([day.month not in range(2, 7) for day in
                        [date + timedelta(i) for i in range(self.get_consecutive_days(date))]])
        else:
            return True
