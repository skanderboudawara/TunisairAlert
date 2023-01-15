"""
Daily Cron job from 7am to Midnight to pull data from the API, clean the SQL and generate the report.
"""
from datetime import datetime

from data_analysis.pillow_reports import generate_report

#!/usr/bin/python3
from data_pipeline.api_requests import AirLabsData

# Adding Airlines
if __name__ == "__main__":

    today = datetime.now()

    airlabs = AirLabsData(today)
    airlabs.get_arrivals()
    airlabs.get_departures()
    airlabs.clean_sql_table(today)

    generate_report(today)
