import sqlite3  # The SQL table will be transformed to pandas
import pandas as pd  # Pandas library
from matplotlib import font_manager as fm  # font manager
import matplotlib.pyplot as plt  # plotlib library
from cycler import cycler  # To define color cycle
import os  # OS
from datetime import datetime  # Datetime
import pytz  # timezone
tz = "Africa/Tunis"


# Path of the font and assign the font to prop
# https://www.1001fonts.com/airport-fonts.html
def get_font_prop(font_name):
    fpath = os.path.join(os.path.abspath(os.curdir),
                         f'reports/fonts/{font_name}')
    return fm.FontProperties(fname=fpath)


def get_df_sql_data(type_flight, todays_date):
    # Path of the SQL Table
    sql_table_loc = path_flight_type = os.path.join(
        os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')
    dat = sqlite3.connect(sql_table_loc)
    query = dat.execute(
        f'SELECT * From TUNISAIR_FLIGHTS WHERE {type_flight}_DATE="{str(todays_date)}" AND FLIGHT_STATUS<>"cancelled"')
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


def create_plot_arr_delay_cumulated():
    '''
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    '''
    # todays date
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    todays_date = current_time.strftime("%d/%m/%Y")

    def create_plot(type_flight):
        # Dataset query

        # Transform the SQL table to pandas + refactor the types
        df = get_df_sql_data(type_flight, todays_date)

        df["DEPARTURE_DELAY"] = df["DEPARTURE_DELAY"].astype(float)
        df["ARRIVAL_DELAY"] = df["ARRIVAL_DELAY"].astype(float)
        # Creating the pivot table
        df_ftype_delay = df[
            [
                f"{type_flight}_DELAY",
                f"{type_flight}_HOUR",
                "FLIGHT_STATUS"
            ]
        ]
        
        df_ftype_delay = df_ftype_delay.pivot_table(
            values=f'{type_flight}_DELAY',
            index=f'{type_flight}_HOUR',
            columns='FLIGHT_STATUS',
            aggfunc='mean'
        ).fillna(0)


        # Creating the figures
        fig, ax = plt.subplots(
            facecolor='black', figsize=((1080/2)/96, 200/96))
        
        df_ftype_delay.plot(kind='bar',
                            ax=ax,
                            stacked=True,
                            # https://matplotlib.org/stable/gallery/color/named_colors.html
                            color={'scheduled': 'orange',
                                   'cancelled': 'lightcoral',
                                   'active': 'skyblue',
                                   'landed': 'white'},
                            )
        #hours = ['00h','01h','02h','03h','04h','05h','06h','07h','08h','09h','10h','11h','12h','13h','14h','15h','16h','17h','18h','19h','20h','21h','22h','23h']
        #plt.xticks(labels=hours)
        # Adjusting the metadata
        ax.set_facecolor('black')
        font_prop = get_font_prop('LEDBDREV.TTF')
        # Title
        ax.set_title(f'AVERAGE {type_flight} delays',
                     fontproperties=font_prop, y=1.2)
        ax.title.set_fontsize(18)
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
