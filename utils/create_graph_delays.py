#!/usr/bin/python
import pytz  # timezone
from datetime import datetime  # Datetime
import os  # OS
from cycler import cycler  # To define color cycle
import matplotlib.pyplot as plt  # plotlib library
from matplotlib import font_manager as fm  # font manager
import sqlite3  # The SQL table will be transformed to pandas
import pandas as pd  # Pandas library
import matplotlib
matplotlib.use('Agg')
tz = "Africa/Tunis"
sql_table_name = "TUN_FLIGHTS"

# Adding Airlines
# Path of the font and assign the font to prop
# https://www.1001fonts.com/airport-fonts.html
def get_font_prop(font_name):
    fpath = os.path.join(os.path.abspath(os.curdir),
                         f'fonts/{font_name}')
    return fm.FontProperties(fname=fpath)


def get_df_sql_data(type_flight, todays_date):
    # Path of the SQL Table
    sql_table_loc = os.path.join(
        os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')
    dat = sqlite3.connect(sql_table_loc)
    query = dat.execute(
        f'SELECT * From {sql_table_name} WHERE {type_flight}_DATE="{str(todays_date)}" AND FLIGHT_STATUS<>"cancelled"')
    cols = [column[0] for column in query.description]
    df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    df = df.convert_dtypes()
    dat.commit()
    dat.close()
    return df


def get_pic_location(current_time, type_flight):
    # Check the directory if it exists
    directory_report_monthly = f'reports/{current_time.strftime("%m")}'
    path_report_save = os.path.join(
        os.path.abspath(os.curdir), directory_report_monthly)
    if not (os.path.isdir(path_report_save)):
        os.mkdir(path_report_save)

    # Save picture and return its path
    return f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_{type_flight[:3]}_delayreport.png'


def create_plot_arr_delay_cumulated(current_time):
    '''
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    '''
    # todays date
    todays_date = current_time.strftime("%d/%m/%Y")

    def create_plot(type_flight):
        # Dataset query

        # Transform the SQL table to pandas + refactor the types
        df = get_df_sql_data(type_flight, todays_date)
        # Creating the pivot table
        df_ftype_delay = df[
            [
                f"{type_flight}_DELAY",
                f"{type_flight}_HOUR",
                "AIRLINE"
            ]
        ].fillna(0).replace('', 0).replace('TU','TUNISAIR').replace('AF','AIR FRANCE').replace('BJ','NOUVELAIR').replace('HV','TRANSAVIA')
        df_ftype_delay[f"{type_flight}_DELAY"] = df_ftype_delay[f"{type_flight}_DELAY"].astype(
            'float64')

        df_ftype_delay = df_ftype_delay.pivot_table(
            values=f'{type_flight}_DELAY',
            index=f'{type_flight}_HOUR',
            columns='AIRLINE',
            aggfunc='mean'
        ).fillna(0)

        # Creating the figures
        fig, ax = plt.subplots(
            facecolor='black', figsize=((1080/2)/96, 200/96))

        df_ftype_delay.plot(kind='bar',
                            ax=ax,
                            # https://matplotlib.org/stable/gallery/color/named_colors.html
                            color={'TUNISAIR': '#D40100',
                                   'AIR FRANCE': 'white',
                                   'NOUVELAIR': '#0054A6',
                                   'TRANSAVIA': '#00D56C'},
                            )
        #hours = ['00h','01h','02h','03h','04h','05h','06h','07h','08h','09h','10h','11h','12h','13h','14h','15h','16h','17h','18h','19h','20h','21h','22h','23h']
        #plt.xticks(labels=hours)
        # Adjusting the metadata
        ax.set_facecolor('black')
        font_prop = get_font_prop('LEDBDREV.TTF')
        # Title
        from_to = 'from' if type_flight=='DEPARTURE' else 'to'
        ax.set_title(f'AVERAGE {type_flight} delays {from_to} TUNISIA',
                     fontproperties=font_prop, y=1.2)
        ax.title.set_fontsize(12)
        ax.title.set_color('orange')

        # legend
        ax.legend(loc='upper center',  bbox_to_anchor=(0.5, 1.25), ncol=3, prop=font_prop,
                  facecolor='black', labelcolor='white', edgecolor='black', handlelength=0.7)

        # Axies and ticks
        ax.set_xlabel(None)
        ax.set_ylabel('Minutes')

        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='x', colors='white')

        # Save figure
        picture_to_save = get_pic_location(current_time, type_flight)
        fig.savefig(picture_to_save, bbox_inches='tight')
        return picture_to_save
    return create_plot('ARRIVAL'), create_plot('DEPARTURE')
