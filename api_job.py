#!/usr/bin/python3
from data_pipeline.api_requests import AirLabsData
from data_analysis.pillow_reports import generate_report
from datetime import datetime

# Adding Airlines
if __name__ == "__main__":
    """
    Daily Cron from 7am to Midnight to pull data from the API
    Clean the SQL
    generate the report
    """
    today = datetime.now()

    airlabs = AirLabsData(today)
    airlabs.get_arrivals()
    airlabs.get_departures()
    airlabs.clean_sql_table(today)

    generate_report(today)
