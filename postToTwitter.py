#!/usr/bin/python
from utils.pillow_reports import generate_report
from pytwitter.post_twitter import post_tweet_with_pic
from utils.sql_func import clean_sql_table
from utils.utility import TimeAttribute


# Adding Airlines
if __name__ == "__main__":
    """_summary_
    Clean the SQL table of yesterday
    Generate the report of yesterday
    Generate the tweet text
    Post the twitter at 9.am
    """
    YESTERDAY_DATE = TimeAttribute().yesterday

    clean_sql_table(YESTERDAY_DATE)

    (
        picture_to_upload,
        nb_delays_arr,
        nb_delays_dep,
        arrival_delayed_max,
        text_worse,
    ) = generate_report(YESTERDAY_DATE)

    tweet_text = f"""
📊 Daily ingest of ✈️  #Tunisair delay performance
Date: {TimeAttribute(YESTERDAY_DATE).dateformat} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival
The worst flight was
🛫{text_worse}🛬
🇹🇳 #Tunisia #Flight #DataAnalyst #Nouvelair #Airfrance #Transavia
    """

    post_tweet_with_pic(
        tweet_text,
        picture_to_upload,
    )
