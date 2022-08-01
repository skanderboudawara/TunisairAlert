#!/usr/bin/python
from utils.tunisair_alert import get_flight
from utils.create_daily_report import create_daily_png_report
from utils.sql_func  import clean_SQL_table
from datetime import datetime
import pytz

tz = "Africa/Tunis"
current_time = datetime.now().astimezone(pytz.timezone(tz))
# Adding Airlines
if __name__ == "__main__":
    get_flight('departure',current_time,True)
    get_flight('arrival',current_time,True)
    clean_SQL_table(current_time)
    create_daily_png_report(current_time)
