#!/usr/bin/python
from utils.create_daily_report import create_daily_png_report
from pytwitter.post_twitter import post_tweet_with_pic
from datetime import datetime, timedelta
import pytz

tz = "Africa/Tunis"
# Adding Airlines
if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)
                 ).astimezone(pytz.timezone(tz))  # To be used for yesterday
    picture_to_upload, nb_delays_arr, nb_delays_dep, arrival_delayed_max, text_worse = create_daily_png_report(
        yesterday)
    post_tweet_with_pic(
        f'📊 Daily ingest of ✈️  #Tunisair delay performance\nDate: {yesterday.strftime("%d-%m-%Y")} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival\nThe worst flight was\n🛫{text_worse}🛬\n#Tunisia #GitHub #Flight #🇹🇳', picture_to_upload)
