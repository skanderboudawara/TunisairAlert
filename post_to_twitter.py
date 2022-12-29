#!/usr/bin/python3
from src.pillow_reports import generate_report
from src.sql_func import SqlManager
from src.utils import TimeAttribute
from src.post_twitter import post_tweet_with_pic
from datetime import datetime, timedelta

# Adding Airlines
if __name__ == "__main__":
    """
    Clean the SQL table of yesterday
    Generate the report of yesterday
    Generate the tweet text
    Post the twitter at 9.am
    """
    yesterday = TimeAttribute(datetime.now() - timedelta(days=1))
    sql_table = SqlManager()

    sql_table.clean_sql_table(yesterday.datetime)

    (picture_to_upload, nb_delays_arr, nb_delays_dep, arrival_delayed_max, text_worse,) = generate_report(yesterday.datetime)

    tweet_text = f"""
📊 Daily ingest of ✈️  #Tunisair delay performance
Date: {yesterday.dateformat} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival
The worst flight was
🛫{text_worse}🛬
🇹🇳 #Tunisia #Flight #DataAnalyst #Nouvelair #Airfrance #Transavia
"""

    post_tweet_with_pic(tweet_text, picture_to_upload)
