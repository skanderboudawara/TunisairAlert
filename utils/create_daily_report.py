from PIL import Image, ImageDraw, ImageFont  # Importing PILLOW
import os  # Create and organize folders
from datetime import datetime  # Importing datime
import pytz  # Importing Timezeon
import sqlite3  # Importing SQLITE 3

######################################
# Function to create the plotlib
#####################################
from utils.create_graph_delays import create_plot_arr_delay_cumulated

# Import necessary fonts
tz = "Africa/Tunis"

# https://www.1001fonts.com/airport-fonts.html
path_skyfont = os.path.join(os.path.abspath(
    os.curdir), 'reports/fonts/LEDBDREV.TTF')
path_skyfont_inverted = os.path.join(
    os.path.abspath(os.curdir), 'reports/fonts/LEDBOARD.TTF')
path_font_glyph_airport = os.path.join(
    os.path.abspath(os.curdir), 'reports/fonts/GlyphyxOneNF.ttf')

# SQL Table
sql_table_loc = path_flight_type = os.path.join(
    os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')



def hex_to_rgb(value):
    '''
    Function to conver HEX color to RGB
    '''
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


def get_text_dimensions(text_string, font):
    '''
    Get text imensions in pixel
    '''
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)


def add_banner(Report, position_l, position_t, label, value):
    '''
    Function to create the label and it's value
    the label will be in orange
    the value will be in white
    '''
    path_skyfont = os.path.join(os.path.abspath(
        os.curdir), 'reports/fonts/LEDBDREV.TTF')
    path_skyfont_inverted = os.path.join(
        os.path.abspath(os.curdir), 'reports/fonts/LEDBOARD.TTF')
    Report.text((position_l+10, position_t), label,
                font=ImageFont.truetype(path_skyfont_inverted, 25), fill='black')
    w, h = get_text_dimensions(
        label, ImageFont.truetype(path_skyfont_inverted, 25))
    Report.text((position_l+w+10, position_t), str(value),
                font=ImageFont.truetype(path_skyfont, 25), fill='white')
    Report.text((position_l+10, position_t), label,
                font=ImageFont.truetype(path_skyfont, 25), fill='orange')


def create_daily_png_report():
    # Create necessary folders and paths
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    todays_date = current_time.strftime("%d/%m/%Y")
    directory_report_monthly = f'reports/{current_time.strftime("%m")}'
    path_report = os.path.join(os.path.abspath(os.curdir), 'reports')
    path_report_save = os.path.join(
        os.path.abspath(os.curdir), directory_report_monthly)
    if not (os.path.isdir(path_report_save)):
        os.mkdir(path_report_save)
    picture_to_save = f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_report.png'

    # Create a white FULL HD picture
    report_img = Image.new('RGB', (1080, 720), color='white')

    # Tunisair LOGO Treatement
    # Adding Tunisair logo
    with Image.open(f'{path_report}/Tunisair_logo.jpg') as tunisair_logo:
        report_img.paste(tunisair_logo, (25, 25))

    Report = ImageDraw.Draw(report_img)

    # Big Title
    Report.text((260, 20), f'TUNISAIR flight report {current_time.strftime("%a %d %b %Y")}', font=ImageFont.truetype(
        path_skyfont, 25), fill='black')
    # Subtitle
    Report.text((260, 55), f'ONLY ON TUNISAIR FLIGHT AND FLEET',
                font=ImageFont.truetype(path_skyfont, 18), fill='black')

    # KPI
    starting_point = 35
    multiplicator = 212
    Report.rectangle((0, 100, 1080, 720), fill='black')

    # SQL Request
    conn = sqlite3.connect(sql_table_loc)
    cursor = conn.cursor()
    sql_success_departure = f'SELECT COUNT(*) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND FLIGHT_STATUS<>"cancelled"'
    sql_departure_delayed = f'SELECT COUNT(*) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND DEPARTURE_DELAY<>""'
    sql_departure_delayed_min = f'SELECT MIN(DEPARTURE_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND DEPARTURE_DELAY<>""'
    sql_departure_delayed_max = f'SELECT MAX(DEPARTURE_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND DEPARTURE_DELAY<>""'
    sql_departure_delayed_avg = f'SELECT AVG(DEPARTURE_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND DEPARTURE_DELAY<>""'
    sql_fail_departure = f'SELECT COUNT(*) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND FLIGHT_STATUS="cancelled"'
    sql_arrival_delayed = f'SELECT COUNT(*) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND ARRIVAL_DELAY<>""'
    sql_arrival_delayed_min = f'SELECT MIN(ARRIVAL_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}"  AND ARRIVAL_DELAY<>""'
    sql_arrival_delayed_max = f'SELECT MAX(ARRIVAL_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}"  AND ARRIVAL_DELAY<>""'
    sql_arrival_delayed_avg = f'SELECT AVG(ARRIVAL_DELAY) FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}"  AND ARRIVAL_DELAY<>""'

    # SQL Execute
    nb_success_departures = cursor.execute(sql_success_departure).fetchone()[0]
    nb_departures_delayed = cursor.execute(sql_departure_delayed).fetchone()[0]
    departures_delayed_min = cursor.execute(
        sql_departure_delayed_min).fetchone()[0]
    departures_delayed_max = cursor.execute(
        sql_departure_delayed_max).fetchone()[0]
    departures_delayed_avg = round(cursor.execute(
        sql_departure_delayed_avg).fetchone()[0], 0)
    nb_fail_flight = cursor.execute(sql_fail_departure).fetchone()[0]
    nb_arrival_delayed = cursor.execute(sql_arrival_delayed).fetchone()[0]
    arrival_delayed_min = cursor.execute(sql_arrival_delayed_min).fetchone()[0]
    arrival_delayed_max = cursor.execute(sql_arrival_delayed_max).fetchone()[0]
    arrival_delayed_avg = round(cursor.execute(
        sql_arrival_delayed_avg).fetchone()[0], 0)

    sql_airport_depart_max = f'SELECT DEPARTURE_IATA FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND ARRIVAL_DELAY!="{str(arrival_delayed_max)}"'
    sql_airport_arrive_max = f'SELECT ARRIVAL_IATA FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND ARRIVAL_DELAY!="{str(arrival_delayed_max)}"'
    sql_worse_flight_number = f'SELECT FLIGHT_NUMBER FROM TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}" AND ARRIVAL_DELAY!="{str(arrival_delayed_max)}"'
    airport_worse_dep = cursor.execute(sql_airport_depart_max).fetchone()[0]
    airport_worse_arr = cursor.execute(sql_airport_arrive_max).fetchone()[0]
    worse_flight_number = cursor.execute(sql_worse_flight_number).fetchone()[0]
    conn.commit()
    conn.close()

    # Adding banners
    start = 120  # Vertical position starting
    add_banner(Report, 25, start, 'TUNISAIR FLIGHTS:', nb_success_departures)
    add_banner(Report, 25, start+40, 'DEPARTURES DELAYED:',
               nb_departures_delayed)
    add_banner(Report, 25, start+40*2, 'MIN DEPARTURES DELAY:',
               f'{str(departures_delayed_min)}m')
    add_banner(Report, 25, start+40*3, 'MAX DEPARTURES DELAY:',
               f'{str(departures_delayed_max)}m')
    add_banner(Report, 25, start+40*4, 'AVG DEPARTURES DELAY:',
               f'{str(departures_delayed_avg)[:-2]}m')
    add_banner(Report, 590, start, 'CANCELLED FLIGHTS:', nb_fail_flight)
    add_banner(Report, 590, start+40, 'ARRIVALS DELAYED:', nb_arrival_delayed)
    add_banner(Report, 590, start+40*2, 'MIN ARRIVAL DELAY:',
               f'{str(arrival_delayed_min)}m')
    add_banner(Report, 590, start+40*3, 'MAX ARRIVAL DELAY:',
               f'{str(arrival_delayed_max)}m')
    add_banner(Report, 590, start+40*4, 'AVG ARRIVAL DELAY:',
               f'{str(arrival_delayed_avg)[:-2]}m')

    # Worse flight
    if arrival_delayed_max > 0:
        # Title to be added if exist
        w, h = get_text_dimensions(f'WORSE FLIGHT: {worse_flight_number}', ImageFont.truetype(path_skyfont, 25))
        add_banner(Report, (1080-w)/2, 340, f'WORSE FLIGHT: ',
                f'{worse_flight_number}')

        # worse flight in DEP ARRIV
        text_worse = str(f'{airport_worse_dep} -----Delay of {str(arrival_delayed_max)}M----> {airport_worse_arr}')
        w, h = get_text_dimensions(text_worse, ImageFont.truetype(path_skyfont, 25))
        position_relative = (1080-w)/2
        # P is symbol of Plane departure with the Glyph Font
        Report.text((position_relative-40, 380), 'Q',font=ImageFont.truetype(path_font_glyph_airport, 25), fill='white')
        Report.text((position_relative, 380), text_worse , font=ImageFont.truetype(path_skyfont, 25), fill='white')
        # Q is symbol of Plane arrival with the Glyph Font
        Report.text((position_relative + w + 10 , 380),'P',font=ImageFont.truetype(path_font_glyph_airport, 25),fill='white')
    else:
        # Title to be added if exist
        w, h = get_text_dimensions(f'ALL FLIGHTS ARE ON TIME', ImageFont.truetype(path_skyfont, 25))
        add_banner(Report, (1080-w)/2, 340, f'ALL FLIGHTS ARE ON TIME',f'') 
        text_worse = str(f'----------')
        w, h = get_text_dimensions(text_worse, ImageFont.truetype(path_skyfont, 25))
        position_relative = (1080-w)/2
        Report.text((position_relative, 380), text_worse , font=ImageFont.truetype(path_skyfont, 25), fill='white')      

    #  Add pandas plot of Cumulated arrival delays
    plot_path_arrival_png = create_plot_arr_delay_cumulated()
    with Image.open(plot_path_arrival_png) as arrival_delay_pic:
        report_img.paste(arrival_delay_pic, (15, 425))
    os.remove(plot_path_arrival_png)
    report_img.save(picture_to_save)
    return picture_to_save

