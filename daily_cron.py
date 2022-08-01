#!/usr/bin/python
from utils.airlabs_imports import get_flight
from utils.pillow_reports import generateReport
from utils.sql_func import clean_SQL_table
from datetime import datetime
import pytz

tz = "Africa/Tunis"
current_time = datetime.now().astimezone(pytz.timezone(tz))
# Adding Airlines
if __name__ == "__main__":
    get_flight("departure", current_time, True)
    get_flight("arrival", current_time, True)
    clean_SQL_table(current_time)
    generateReport(current_time)
