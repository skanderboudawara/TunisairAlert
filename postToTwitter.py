#!/usr/bin/python
from utils.pillow_reports import generate_report
from pytwitter.post_twitter import post_tweet_with_pic
from utils.sql_func import clean_sql_table
from datetime import datetime, timedelta
import pytz

TUNISIA_TZ = "Africa/Tunis"
YESTERDAY_DATE = (datetime.now() - timedelta(days=1)).astimezone(
    pytz.timezone(TUNISIA_TZ)
)  # To be used for YESTERDAY_DATE

# Adding Airlines
if __name__ == "__main__":

    clean_sql_table(YESTERDAY_DATE)
    (
        picture_to_upload,
        nb_delays_arr,
        nb_delays_dep,
        arrival_delayed_max,
        text_worse,
    ) = generate_report(YESTERDAY_DATE)
    post_tweet_with_pic(
        f"""
📊 Daily ingest of ✈️  #Tunisair delay performance
Date: {YESTERDAY_DATE.strftime("%d-%m-%Y")} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival
The worst flight was
🛫{text_worse}🛬
🇹🇳 #Tunisia #Flight #DataAnalyst #Nouvelair #Airfrance #Transavia
    """,
        picture_to_upload,
    )
