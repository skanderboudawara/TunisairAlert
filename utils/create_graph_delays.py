import sqlite3  # The SQL table will be transformed to pandas
import pandas as pd  # Pandas library
from matplotlib import font_manager as fm  # font manager
import matplotlib.pyplot as plt  # plotlib library
from cycler import cycler  # To define color cycle
import os  # OS
from datetime import datetime  # Datetime
import pytz  # timezone
tz = "Africa/Tunis"

# Path of the SQL Table
sql_table_loc = path_flight_type = os.path.join(
    os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')

# Path of the font and assign the font to prop
# https://www.1001fonts.com/airport-fonts.html
fpath = os.path.join(os.path.abspath(os.curdir), 'reports/fonts/LEDBDREV.TTF')
prop = fm.FontProperties(fname=fpath)


def create_plot_arr_delay_cumulated():
    '''
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    '''
    # todays date
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    todays_date = current_time.strftime("%d/%m/%Y")

    # Dataset query
    dat = sqlite3.connect(sql_table_loc)
    query = dat.execute(
        f'SELECT * From TUNISAIR_FLIGHTS WHERE DEPARTURE_DATE="{str(todays_date)}"')
    cols = [column[0] for column in query.description]

    # Transform the SQL table to pandas + refactor the types
    df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    df = df.convert_dtypes()
    df["DEPARTURE_DELAY"] = pd.to_numeric(df["DEPARTURE_DELAY"])
    df["ARRIVAL_DELAY"] = pd.to_numeric(df["ARRIVAL_DELAY"])

    def create_plot(type_flight):
        # Creating the pivot table
        df_ftype_delay = df[[f"{type_flight}_DELAY",
                           f"{type_flight}_HOUR", "FLIGHT_STATUS"]]
        df_ftype_delay = df_ftype_delay.pivot_table(values=f'{type_flight}_DELAY',
                                                index=f'{type_flight}_HOUR',
                                                columns='FLIGHT_STATUS', aggfunc='sum')
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
                                 'landed': 'white'}

                          )
        # Adjusting the metadata
        ax.set_facecolor('black')
        ax.set_title(f'Cumulated {type_flight} delays', fontproperties=prop, y=1.2)
        ax.title.set_fontsize(18)
        ax.title.set_color('orange')

        ax.legend(loc='upper center',  bbox_to_anchor=(0.5, 1.25),
                  ncol=3, prop=prop, facecolor='black', labelcolor='white', edgecolor='black', handlelength=0.7)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.set_xlabel(None)
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='x', colors='white')

        # Check the directory if it exists
        directory_report_monthly = f'reports/{current_time.strftime("%m")}'
        path_report_save = os.path.join(
            os.path.abspath(os.curdir), directory_report_monthly)
        if not (os.path.isdir(path_report_save)):
            os.mkdir(path_report_save)

        # Save picture and return its path
        picture_to_save = f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_{type_flight[:3]}_delayreport.png'
        fig.savefig(picture_to_save, bbox_inches='tight')
        return picture_to_save
    return create_plot('ARRIVAL'), create_plot('DEPARTURE')
