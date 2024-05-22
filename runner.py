import pprint
from datetime import date

from call_scheduler import CallScheduler

if __name__ == '__main__':
    scheduler = CallScheduler(start_date=date(2024, 7, 1), end_date=date(2025, 6, 30))
    scheduler.create_schedule()
    pprint.pp(
        {scheduler.schedule.residents[id].name: load for id, load in
         scheduler.schedule.total_stats.resident_load.items()})
