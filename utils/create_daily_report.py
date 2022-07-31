#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont  # Importing PILLOW
import os  # Create and organize folders
from datetime import datetime  # Importing datime
import pytz  # Importing Timezeon
import sqlite3  # Importing SQLITE 3

# Adding Airlines
######################################
# Function to create the plotlib
#####################################
from utils.create_graph_delays import create_plot_arr_delay_cumulated

# Import necessary fonts
tz = "Africa/Tunis"
airline_name = {
            'TU': 'TUNISAIR',
            'AF': 'AIR FRANCE',
            'BJ' : 'NOUVELAIR',
            'HV' : 'TRANSAVIA'
        }
font_size = 20
# https://www.1001fonts.com/airport-fonts.html
path_skyfont = os.path.join(os.path.abspath(
    os.curdir), 'fonts/LEDBDREV.TTF')
path_skyfont_inverted = os.path.join(
    os.path.abspath(os.curdir), 'fonts/LEDBOARD.TTF')
path_font_glyph_airport = os.path.join(
    os.path.abspath(os.curdir), 'fonts/GlyphyxOneNF.ttf')

# SQL Table
sql_table_loc = os.path.join(os.path.abspath(
    os.curdir), 'datasets/SQL table/tunisair_delay.db')
sql_table_name = "TUN_FLIGHTS"


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
        os.curdir), 'fonts/LEDBDREV.TTF')
    path_skyfont_inverted = os.path.join(
        os.path.abspath(os.curdir), 'fonts/LEDBOARD.TTF')
    Report.text((position_l+10, position_t), label,
                font=ImageFont.truetype(path_skyfont_inverted, font_size), fill='black')
    w, h = get_text_dimensions(
        label, ImageFont.truetype(path_skyfont_inverted, font_size))
    Report.text((position_l+w+10, position_t), str(value),
                font=ImageFont.truetype(path_skyfont, font_size), fill='white')
    Report.text((position_l+10, position_t), label,
                font=ImageFont.truetype(path_skyfont, font_size), fill='orange')


def get_picture_to_save_loc(current_time):
    directory_report_monthly = f'reports/{current_time.strftime("%m")}'

    path_report_save = os.path.join(
        os.path.abspath(os.curdir), directory_report_monthly)
    if not (os.path.isdir(path_report_save)):
        os.mkdir(path_report_save)
    return f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_report.png'


def create_daily_png_report(current_time):
    # Create necessary folders and paths
    todays_date = current_time.strftime("%d/%m/%Y")
    path_report = os.path.join(os.path.abspath(os.curdir), 'reports')
    picture_to_save = get_picture_to_save_loc(current_time)
    # Create a white FULL HD picture
    report_img = Image.new('RGB', (1080, 720), color='white')

    # Tunisair LOGO Treatement
    # Adding Tunisair logo
    with Image.open('tunisair_alert_logo.png') as tunisair_logo:
        report_img.paste(tunisair_logo, (25, 25))

    Report = ImageDraw.Draw(report_img)

    # Big Title
    Report.text((260, 15), f'TUNISAIR flight report {current_time.strftime("%a %d %b %Y")}', font=ImageFont.truetype(
        path_skyfont, 25), fill='black')
    # Subtitle
    Report.text((260, 50), f'SCOPE FROM/TO TUNISIA\nAIRLINES: TUNISAIR - NOUVELAIR - AIR FRANCE - TRANSAVIA',
                font=ImageFont.truetype(path_skyfont, 15), fill='black')

    # KPI
    Report.rectangle((0, 100, 1080, 720), fill='black')

    # SQL Request
    h_start = 120  # Vertical position starting
    v_start_dep = 25
    v_start_arr = 570
    conn = sqlite3.connect(sql_table_loc)
    cursor = conn.cursor()

    sql_success_departure = f'SELECT COUNT(*) FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}" AND AIRLINE="TU"  AND FLIGHT_STATUS<>"cancelled"'
    nb_success_departures = cursor.execute(sql_success_departure).fetchone()[0]
    add_banner(Report, v_start_dep, h_start,
               'TUNISAIR FLIGHTS:', nb_success_departures)

    sql_fail_departure = f'SELECT COUNT(*) FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}" AND AIRLINE="TU" AND FLIGHT_STATUS="cancelled"'
    nb_fail_flight = cursor.execute(sql_fail_departure).fetchone()[0]
    add_banner(Report, v_start_arr, h_start,
               'TUNISAIR CANCELLED FLIGHTS:', nb_fail_flight)

    type_flights = ['DEPARTURE', 'ARRIVAL']
    sql_operators = ['COUNT', 'MIN', 'MAX', 'AVG']

    for type_f in type_flights:
        for index_op, sql_op in enumerate(sql_operators):
            query_op = 'COUNT(*)' if sql_op == 'COUNT' else f'{sql_op}({type_f}_DELAY)'
            query_sql = f'SELECT {query_op} FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}"  AND {type_f}_DELAY<>"0" AND {type_f}_DELAY<>"" AND FLIGHT_STATUS<>"cancelled"'
            sql_execute_query = cursor.execute(query_sql).fetchone()[0]
            result_fetch = 0 if (sql_execute_query is None) | (
                sql_execute_query == '') else sql_execute_query
            result_fetch = int(round(result_fetch, 0))
            if (sql_op == 'MAX') & (type_f == 'ARRIVAL'):
                arrival_delayed_max = result_fetch
            elif (sql_op == 'COUNT') & (type_f == 'ARRIVAL'):
                nb_delays_arr = result_fetch
            elif (sql_op == 'COUNT') & (type_f == 'DEPARTURE'):
                nb_delays_dep = result_fetch
            v_start = v_start_dep if type_f == 'DEPARTURE' else v_start_arr
            h_start_bytype = h_start + (40*(index_op+1))
            sql_op_txt = 'NB' if sql_op == 'COUNT' else sql_op
            add_banner(Report,
                       v_start,
                       h_start_bytype,
                       f'{sql_op_txt} {type_f} DELAY:',
                       f'{result_fetch}{"M" if sql_op_txt != "NB" else ""}'
                       )

    sql_worse_flight = f'''
    SELECT DEPARTURE_IATA, ARRIVAL_IATA, FLIGHT_NUMBER, AIRLINE
    FROM {sql_table_name} 
    WHERE DEPARTURE_DATE="{str(todays_date)}" 
     
    AND ARRIVAL_DELAY="{str(arrival_delayed_max)}" 
    AND FLIGHT_STATUS="landed"
    '''
    worse_flight = [] if arrival_delayed_max == 0 else cursor.execute(
        sql_worse_flight).fetchone()
    conn.commit()
    conn.close()
    
    # Worse flight
    if arrival_delayed_max > 0:
        airport_worse_dep = worse_flight[0]
        airport_worse_arr = worse_flight[1]
        worse_flight_number = worse_flight[2]
        worse_airline = airline_name[worse_flight[3]]
        
        # Title to be added if exist
        w_label, h_label = get_text_dimensions(
            f'WORST FLIGHT: {worse_airline} {worse_flight_number}', ImageFont.truetype(path_skyfont, 20))
        add_banner(Report, (1080-w_label)/2, 340,
                   f'WORST FLIGHT:', f'{worse_airline} {worse_flight_number}')

        # worse flight in DEP ARRIV
        text_worse = str(
            f'{airport_worse_dep} -----Delay of {str(arrival_delayed_max)}M----> {airport_worse_arr}')
        
        w_value, h_value = get_text_dimensions(
            text_worse, ImageFont.truetype(path_skyfont, font_size))
        position_relative = (1080-w_value)/2
        # P is symbol of Plane departure with the Glyph Font
        Report.text((position_relative-40, 340+h_label+15), 'Q',
                    font=ImageFont.truetype(path_font_glyph_airport, font_size), fill='white')
        Report.text((position_relative, 340+h_label+15), text_worse,
                    font=ImageFont.truetype(path_skyfont, font_size), fill='white')
        # Q is symbol of Plane arrival with the Glyph Font
        Report.text((position_relative + w_value + 10, 340+h_label+15), 'P',
                    font=ImageFont.truetype(path_font_glyph_airport, font_size), fill='white')
    else:
        # Title to be added if exist
        w_label, h_label = get_text_dimensions(
            f'ALL FLIGHTS ARE ON TIME', ImageFont.truetype(path_skyfont, font_size))
        add_banner(Report, (1080-w_label)/2, 340,
                   f'ALL FLIGHTS ARE ON TIME', f'')
        text_worse = str(f'----------')
        w_value, h_value = get_text_dimensions(
            text_worse, ImageFont.truetype(path_skyfont, font_size))
        position_relative = (1080-w_value)/2
        Report.text((position_relative, 340+h_label+10), text_worse,
                    font=ImageFont.truetype(path_skyfont, font_size), fill='white')

    #  Add pandas plot of Cumulated arrival delays
    plot_path_arrival_png, plot_path_departure_png = create_plot_arr_delay_cumulated(
        current_time)
    with Image.open(plot_path_departure_png) as departure_delay_pic:
        report_img.paste(departure_delay_pic, (15, 425))
    os.remove(plot_path_departure_png)

    with Image.open(plot_path_arrival_png) as arrival_delay_pic:
        report_img.paste(arrival_delay_pic, (545, 425))
    os.remove(plot_path_arrival_png)

    report_img.save(picture_to_save)
    return picture_to_save, nb_delays_arr, nb_delays_dep, arrival_delayed_max, text_worse
