#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont  # Importing PILLOW
import os  # Create and organize folders
import sqlite3  # Importing SQLITE 3

# Adding Airlines
######################################
# Function to create the plotlib
#####################################
from utils.matplotlib_graphs import (
    plot_from_to_airport,
    plot_tunisair_arrival_dep_delays,
)

# CONST
# Import necessary fonts
TUNISIA_TZ = "Africa/Tunis"
AIRLINE_NAMES = {
    "TU": "TUNISAIR",
    "AF": "AIR FRANCE",
    "BJ": "NOUVELAIR",
    "HV": "TRANSAVIA",
}
FLIGHT_STATUS = ["scheduled", "cancelled", "active", "landed"]
TYPE_FLIGHTS = ["DEPARTURE", "ARRIVAL"]
SQL_OPERATORS = ["MIN", "MAX", "AVG"]
FONT_SIZE = 20
# https://www.1001fonts.com/airport-fonts.html
PATH_SKYFONT = os.path.join(os.path.abspath(os.curdir), "fonts/LEDBDREV.TTF")
PATH_SKYFONT_INVERTED = os.path.join(os.path.abspath(os.curdir), "fonts/LEDBOARD.TTF")
PATH_GLYPH_AIRPORT = os.path.join(os.path.abspath(os.curdir), "fonts/GlyphyxOneNF.ttf")

# SQL Table
PATH_SQL_DB = os.path.join(
    os.path.abspath(os.curdir), "datasets/SQL table/tunisair_delay.db"
)
sql_table_name = "TUN_FLIGHTS"


def get_text_dimensions(text_string, font):
    """
    Get text imensions in pixel
    params
    @text_string : the string that will writtent -> str
    @font : the pillow imagefont -> ImageFont.truetype
    """
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)


def add_banner(report, x, y, label, value):
    """
    Function to create the label and it's value
    the label will be in orange
    the value will be in white
    params
    @report : the report image pillow -> Image
    @x : the x position -> int
    @y : the y position -> int
    @label : the label string will be in orange -> str
    @value : the value of the label will be in white -> str
    """
    report.text(
        (x + 10, y),
        label,
        font=ImageFont.truetype(PATH_SKYFONT_INVERTED, FONT_SIZE),
        fill="black",
    )
    w, h = get_text_dimensions(
        label, ImageFont.truetype(PATH_SKYFONT_INVERTED, FONT_SIZE)
    )
    report.text(
        (x + w + 10, y),
        str(value),
        font=ImageFont.truetype(PATH_SKYFONT, FONT_SIZE),
        fill="white",
    )
    report.text(
        (x + 10, y),
        label,
        font=ImageFont.truetype(PATH_SKYFONT, FONT_SIZE),
        fill="orange",
    )

    return get_text_dimensions(
        f"{label} {value}", ImageFont.truetype(PATH_SKYFONT, FONT_SIZE)
    )


def get_picture_to_save_loc(current_time):
    """
    To create the dir and prepare the save of the report png
    params
    @current_time : the current time -> datetime
    """
    directory_report_monthly = f'reports/{current_time.strftime("%m")}'

    path_report_save = os.path.join(
        os.path.abspath(os.curdir), directory_report_monthly
    )
    if not (os.path.isdir(path_report_save)):
        os.mkdir(path_report_save)
    return f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_report.png'


def generate_report(current_time):
    """
    Function to generate the daily report as function of current time
    params
    @current_time : the current time -> datetime
    """

    # Create necessary folders and paths
    todays_date = current_time.strftime("%d/%m/%Y")
    picture_to_save = get_picture_to_save_loc(current_time)
    report_img = Image.new("RGB", (1080, 720), color="white")

    """
    ###########################
    # LOGO BLOCK
    ###########################
    """
    with Image.open("tunisair_alert_logo.png") as tunisair_logo:
        report_img.paste(tunisair_logo, (25, 7))

    """
    ###########################
    # TITLES BLOCKS
    ###########################
    """

    # Draw picture
    report = ImageDraw.Draw(report_img)

    # Last update hour
    report.text(
        (55, 60),
        f'LAST UPDATE AT {current_time.strftime("%H:%M")}',
        font=ImageFont.truetype(PATH_SKYFONT, 9),
        fill="black",
    )
    # Big Title
    report.text(
        (260, 10),
        f'TUNISAIR DAILY INGEST {current_time.strftime("%a %d %b %Y")}',
        font=ImageFont.truetype(PATH_SKYFONT, 25),
        fill="black",
    )
    # Subtitle
    report.text(
        (260, 50),
        "SCOPE FROM/TO Tunis-Carthage International Airport",
        font=ImageFont.truetype(PATH_SKYFONT, 15),
        fill="black",
    )
    """
    ###########################
    # KPI BLOCKS
    ###########################
    """
    h_start = 80  # horizontal position
    report.rectangle((0, h_start, 1080, 720), fill="black")

    # Positions
    h_start = h_start + 15  # horizonta  position starting
    v_start_dep = 15  # vertical position for DEPARTURES
    v_start_arr = 580  # vertical position for ARRIVALS

    # SQL Requests
    conn = sqlite3.connect(PATH_SQL_DB)
    cursor = conn.cursor()

    w, h = add_banner(report, v_start_dep, h_start, "TUNISAIR FLIGHTS", "")

    v_start = v_start_dep + w + 10

    # To get the repartition count by flight status
    for status in FLIGHT_STATUS:
        sql_status = f'SELECT COUNT(*) FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}" AND AIRLINE="TU"  AND FLIGHT_STATUS="{status}"'
        count_sql_status = cursor.execute(sql_status).fetchone()[0]
        w, h = add_banner(report, v_start, h_start, f"{status}:", count_sql_status)
        v_start = v_start + w + 10

    # To prepare the KPI of counting in Departure & Counting in Arrivals
    # 2 rounded rectangles that will contain the KPIs
    for rounded_start in [v_start_arr, v_start_dep]:
        report.rounded_rectangle(
            (rounded_start, h_start + 35, rounded_start + 480, h_start + 115),
            radius=20,
            outline="orange",
        )

    for type_f in TYPE_FLIGHTS:
        h_start_bytype = h_start + 45
        v_start = (v_start_dep if type_f == "DEPARTURE" else v_start_arr) + 50

        # Counting how many delays
        sql_count = f'SELECT COUNT(*) FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}" AND AIRLINE="TU" AND {type_f}_DELAY<>"0" AND {type_f}_DELAY<>"" AND FLIGHT_STATUS<>"cancelled"'
        count_nb = cursor.execute(sql_count).fetchone()[0]
        if type_f == "DEPARTURE":
            nb_delays_dep = count_nb
        if type_f == "ARRIVAL":
            nb_delays_arr = count_nb
        w, h = add_banner(
            report, v_start + 30, h_start_bytype, f"DELAYED {type_f}:", f"{count_nb}"
        )
        h_start_bytype = h_start + 85

        # add more info on MIN MAX AVG
        for sql_op in SQL_OPERATORS:
            query_sql = f'SELECT {sql_op}({type_f}_DELAY) FROM {sql_table_name} WHERE DEPARTURE_DATE="{str(todays_date)}" AND AIRLINE="TU" AND {type_f}_DELAY<>"0" AND {type_f}_DELAY<>"" AND FLIGHT_STATUS<>"cancelled"'
            sql_execute_query = cursor.execute(query_sql).fetchone()[0]
            result_fetch = (
                0
                if (sql_execute_query is None) | (sql_execute_query == "")
                else sql_execute_query
            )
            result_fetch = int(round(result_fetch, 0))
            if (sql_op == "MAX") & (type_f == "ARRIVAL"):
                max_arrival_delay = result_fetch
            w, h = add_banner(
                report, v_start, h_start_bytype, f"{sql_op}:", f"{result_fetch}M"
            )
            v_start = v_start + w

    # Get the information of WORSE Flight
    sql_worse_flight = f"""
                        SELECT DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, FLIGHT_NUMBER, AIRLINE
                        FROM {sql_table_name} 
                        WHERE DEPARTURE_DATE="{str(todays_date)}" 
                        AND AIRLINE="TU"
                        AND ARRIVAL_DELAY="{str(max_arrival_delay)}" 
                        AND FLIGHT_STATUS<>"cancelled"
                        """
    worse_flight = (
        [] if max_arrival_delay == 0 else cursor.execute(sql_worse_flight).fetchone()
    )
    conn.commit()
    conn.close()

    # Worse flight
    h_worse_flight = h_start + 125
    if max_arrival_delay > 0:
        airport_worse_dep = worse_flight[0]
        airport_worse_arr = worse_flight[1]
        worse_flight_number = worse_flight[2]
        worse_airline = AIRLINE_NAMES[worse_flight[3]]

        # Title to be added if exist
        w_label, h_label = get_text_dimensions(
            f"WORST FLIGHT: {worse_airline} {worse_flight_number}",
            ImageFont.truetype(PATH_SKYFONT, 20),
        )
        add_banner(
            report,
            (1080 - w_label) / 2,
            h_worse_flight,
            f"WORST FLIGHT:",
            f"{worse_airline} {worse_flight_number}",
        )

        # worse flight in DEP ARRIV
        text_worse_flight = str(
            f"{airport_worse_dep} -----Delay of {str(max_arrival_delay)}M----> {airport_worse_arr}"
        )

        w_value, h_value = get_text_dimensions(
            text_worse_flight, ImageFont.truetype(PATH_SKYFONT, FONT_SIZE)
        )
        position_relative = (1080 - w_value) / 2
        # P is symbol of Plane departure with the Glyph Font
        report.text(
            (position_relative - 40, h_worse_flight + h_label + 15),
            "Q",
            font=ImageFont.truetype(PATH_GLYPH_AIRPORT, FONT_SIZE),
            fill="white",
        )
        report.text(
            (position_relative, h_worse_flight + h_label + 15),
            text_worse_flight,
            font=ImageFont.truetype(PATH_SKYFONT, FONT_SIZE),
            fill="white",
        )
        # Q is symbol of Plane arrival with the Glyph Font
        report.text(
            (position_relative + w_value + 10, h_worse_flight + h_label + 15),
            "P",
            font=ImageFont.truetype(PATH_GLYPH_AIRPORT, FONT_SIZE),
            fill="white",
        )
    else:
        # Title to be added if exist
        w_label, h_label = get_text_dimensions(
            f"ALL FLIGHTS ARE ON TIME", ImageFont.truetype(PATH_SKYFONT, FONT_SIZE)
        )
        add_banner(
            report,
            (1080 - w_label) / 2,
            h_worse_flight,
            f"ALL FLIGHTS ARE ON TIME",
            f"",
        )
        text_worse_flight = str(f"----------")
        w_value, h_value = get_text_dimensions(
            text_worse_flight, ImageFont.truetype(PATH_SKYFONT, FONT_SIZE)
        )
        position_relative = (1080 - w_value) / 2
        report.text(
            (position_relative, h_worse_flight + h_label + 10),
            text_worse_flight,
            font=ImageFont.truetype(PATH_SKYFONT, FONT_SIZE),
            fill="white",
        )

    """
    ###########################
    # PLOT BLOCKS
    ###########################
    """

    def past_plots(report_img, x, y, plot_pic):
        """
        to past plots from matplotlib to the report
        @report_img the report from PILLOW -> Image
        @x position in x -> int
        @y position in y -> int
        @plot_pic the path of the plot picture generated by Matplotlib -> str
        """
        with Image.open(plot_pic) as plot_img:
            report_img.paste(plot_img, (x, y))
        os.remove(plot_pic)
        return report_img

    #  Add pandas plot of Cumulated arrival delays

    past_plots(
        report_img, v_start_dep, 290, plot_tunisair_arrival_dep_delays(current_time)
    )
    path_plot_arrival_delays, path_plot_departure_delays = plot_from_to_airport(
        current_time
    )
    plot_h_pos = 470
    past_plots(report_img, v_start_dep, plot_h_pos, path_plot_departure_delays)
    past_plots(report_img, 530, plot_h_pos, path_plot_arrival_delays)
    report.rounded_rectangle((v_start_dep, 290, 1060, 705), radius=20, outline="orange")

    report_img.save(picture_to_save)
    print(f"Daily report created for {current_time}")
    return (
        picture_to_save,
        nb_delays_arr,
        nb_delays_dep,
        max_arrival_delay,
        text_worse_flight,
    )
