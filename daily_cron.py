from utils.tunisair_alert import get_flight
from utils.create_daily_report import create_daily_png_report
from post_to_twitter.post_tweet_with_image import post_tweet_with_pic
from datetime import datetime
import pytz

tz = "Africa/Tunis"
current_time = datetime.now().astimezone(pytz.timezone(tz))

#get_flight('departure',True)
#get_flight('arrival',True)
picture_to_upload, nb_delays_arr, nb_delays_dep, arrival_delayed_max, text_worse = create_daily_png_report()
post_tweet_with_pic(f'📊 Daily ingest of ✈️  #Tunisair delay performance\nDate: {current_time.strftime("%d-%m-%Y")} with {nb_delays_dep} #delayed_departure and {nb_delays_arr} #delayed_arrival\nThe worst flight was\n🛫{text_worse}🛬\n#Tunisia #GitHub #Flight #🇹🇳',picture_to_upload)

