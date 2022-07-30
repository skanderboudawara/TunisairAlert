from utils.tunisair_alert import get_flight
from utils.create_daily_report import create_daily_png_report


get_flight('departure',True)
get_flight('arrival',True)
create_daily_png_report()