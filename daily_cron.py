#!/usr/bin/python
from utils.airlabs_imports import get_flights
from utils.pillow_reports import generate_report
from utils.sql_func import clean_sql_table
from datetime import datetime
import pytz

TUNISIA_TZ = "Africa/Tunis"
TODAY_DATE = datetime.now().astimezone(pytz.timezone(TUNISIA_TZ))
# Adding Airlines
if __name__ == "__main__":
    get_flights("departure", TODAY_DATE, True)
    get_flights("arrival", TODAY_DATE, True)
    clean_sql_table(TODAY_DATE)
    generate_report(TODAY_DATE)
