#!/usr/bin/python
from utils.pillow_reports import generateReport
from pytwitter.post_twitter import post_tweet_with_pic
from utils.sql_func import clean_SQL_table
from datetime import datetime, timedelta
import pytz

tz = "Africa/Tunis"
# Adding Airlines
if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).astimezone(
        pytz.timezone(tz)
    )  # To be used for yesterday
    clean_SQL_table(yesterday)
    (
        picture_to_upload,
        nb_delays_arr,
        nb_delays_dep,
        arrival_delayed_max,
        text_worse,
    ) = generateReport(yesterday)
    post_tweet_with_pic(
        f"""
📊 Daily ingest of ✈️  #Tunisair delay performance
Date: {yesterday.strftime("%d-%m-%Y")} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival
The worst flight was
🛫{text_worse}🛬
🇹🇳 #Tunisia #GitHub #Flight #DataAnalyst #Performance
    """,
        picture_to_upload,
    )
