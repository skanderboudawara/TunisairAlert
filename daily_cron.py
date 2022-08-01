#!/usr/bin/python
from utils.airlabs_imports import get_flights
from utils.pillow_reports import generate_report
from utils.sql_func import clean_sql_table
from utils.utility import TimeAttribute

# Adding Airlines
if __name__ == "__main__":
    today = TimeAttribute().today
    get_flights("departure", today)
    get_flights("arrival", today)
    clean_sql_table(today)
    generate_report(today)
