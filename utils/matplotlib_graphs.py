#!/usr/bin/python
from datetime import datetime  # Datetime
import os  # OS
from cycler import cycler  # To define color cycle
import matplotlib.pyplot as plt  # plotlib library
from matplotlib import font_manager as fm, markers  # font manager
import sqlite3  # The SQL table will be transformed to pandas
import pandas as pd  # Pandas library
import matplotlib

matplotlib.use("Agg")
SQL_TABLE_NAME = "TUN_FLIGHTS"

# Adding Airlines
# Path of the font and assign the font to prop
# https://www.1001fonts.com/airport-fonts.html


def get_font_prop(font_name):
    """
    @font_name : name of font as is in fonts folder -> str
    """
    fpath = os.path.join(os.path.abspath(os.curdir), f"fonts/{font_name}")
    return fm.FontProperties(fname=fpath)


def get_df_sql_data(current_time, type_flight):
    """
    param
    @current_time : current time in datetime format -> datetime
    @type_flight: DEPARTURE or ARRIVAL -> str
    """
    # todays date
    todays_date = current_time.strftime("%d/%m/%Y")
    # Path of the SQL Table
    PATH_SQL_DB = os.path.join(
        os.path.abspath(os.curdir), "datasets/SQL table/tunisair_delay.db"
    )
    dat = sqlite3.connect(PATH_SQL_DB)
    query = dat.execute(
        f'SELECT * FROM {SQL_TABLE_NAME} WHERE {type_flight}_DATE="{str(todays_date)}" AND FLIGHT_STATUS<>"cancelled"'
    )
    cols = [column[0] for column in query.description]

    df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    df = df.convert_dtypes()
    dat.commit()
    dat.close()
    return df


def get_pic_location(current_time, name="DELAY", type_flight="DEPARTURE"):
    """
    param
    @current_time : current time in datetime format -> datetime
    @type_flight: DEPARTURE or ARRIVAL -> str
    """
    # Check the directory if it exists
    directory_report_monthly = f'reports/{current_time.strftime("%m")}'
    path_report_save = os.path.join(
        os.path.abspath(os.curdir), directory_report_monthly
    )
    if not (os.path.isdir(path_report_save)):
        os.mkdir(path_report_save)

    # Save picture and return its path
    return f'{path_report_save}/{current_time.strftime("%d_%m_%Y")}_{type_flight[:3]}_{name}.png'


def plot_from_to_airport(current_time):
    """
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    Param
    @current_time: current ttime datetime format -> datetime
    """

    def create_plot(type_flight, from_airport, to_airport):
        """
        param
        @type_flight : ARRIVAL or DEPARTURE -> str
        @from_airport: Airport country in english full letters -> str
        @to_airport: Airport country in english full letters -> str
        """
        # Transform the SQL table to pandas + refactor the types
        df = get_df_sql_data(current_time, type_flight)
        df = df[
            (df["ARRIVAL_COUNTRY"] == to_airport)
            & (df["DEPARTURE_COUNTRY"] == from_airport)
        ]
        # Creating the pivot table
        df_ftype_delay = df[[f"{type_flight}_DELAY", f"{type_flight}_HOUR", "AIRLINE"]]
        df_ftype_delay = (
            df_ftype_delay.fillna(0)
            .replace("", 0)
            .replace("TU", "TUNISAIR")
            .replace("AF", "AIR FRANCE")
            .replace("BJ", "NOUVELAIR")
            .replace("TO", "TRANSAVIA")
        )
        df_ftype_delay[f"{type_flight}_DELAY"] = df_ftype_delay[
            f"{type_flight}_DELAY"
        ].astype("float64")

        df_ftype_delay = df_ftype_delay.pivot_table(
            values=f"{type_flight}_DELAY",
            index=f"{type_flight}_HOUR",
            columns="AIRLINE",
            aggfunc="mean",
        ).fillna(0)

        # Creating the figures
        fig, ax = plt.subplots(facecolor="black", figsize=((1100 / 2) / 96, 160 / 96))

        df_ftype_delay.plot(
            kind="bar",
            ax=ax,
            # https://matplotlib.org/stable/gallery/color/named_colors.html
            color={
                "TUNISAIR": "#D40100",
                "AIR FRANCE": "white",
                "NOUVELAIR": "#0054A6",
                "TRANSAVIA": "#00D56C",
            },
        )

        # Adjusting the metadata
        ax.set_facecolor("black")
        font_prop = get_font_prop("LEDBDREV.TTF")
        # Title
        from_to = "from" if type_flight == "DEPARTURE" else "to"
        ax.set_title(
            f"AVERAGG DELAY from {from_airport} -> {to_airport}",
            fontproperties=font_prop,
            y=1.2,
        )
        ax.title.set_fontsize(12)
        ax.title.set_color("orange")

        # legend
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.25),
            ncol=3,
            prop=font_prop,
            facecolor="black",
            labelcolor="white",
            edgecolor="black",
            handlelength=0.7,
        )

        # Axies and ticks
        ax.set_xlabel(None)
        ax.set_ylabel("Minutes")

        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.tick_params(axis="y", colors="white")
        ax.tick_params(axis="x", colors="white")

        # Save figure
        picture_to_save = get_pic_location(current_time, "delayreport", type_flight)
        fig.savefig(picture_to_save, bbox_inches="tight")
        return picture_to_save

    return create_plot("ARRIVAL", "FRANCE", "TUNISIA"), create_plot(
        "DEPARTURE", "TUNISIA", "FRANCE"
    )


def plot_tunisair_arrival_dep_delays(current_time):
    """
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    Param
    @current_time: current ttime datetime format -> datetime
    """
    # Transform the SQL table to pandas + refactor the types
    df = get_df_sql_data(current_time, "DEPARTURE")
    df = df[(df["AIRLINE"] == "TU")]
    # Creating the pivot table
    df_ftype_delay = df[
        [
            "DEPARTURE_DELAY",
            "ARRIVAL_DELAY",
            "DEPARTURE_HOUR",
        ]
    ]
    df_ftype_delay = df_ftype_delay.fillna(0).replace("", 0)
    df_ftype_delay["DEPARTURE_DELAY"] = df_ftype_delay["DEPARTURE_DELAY"].astype(
        "float64"
    )
    df_ftype_delay["ARRIVAL_DELAY"] = df_ftype_delay["ARRIVAL_DELAY"].astype("float64")
    df_ftype_delay = df_ftype_delay.rename(
        columns={"DEPARTURE_DELAY": "AVG DEP DELAY", "ARRIVAL_DELAY": "AVG ARR DELAY"}
    )
    df_ftype_delay = df_ftype_delay.fillna(0).replace("", 0)
    list_dep = list(df_ftype_delay["DEPARTURE_HOUR"].unique())
    df_ftype_delay = df_ftype_delay.groupby(["DEPARTURE_HOUR"]).mean().fillna(0)
    # Creating the figures
    fig, ax = plt.subplots(facecolor="black", figsize=((1200) / 96, 110 / 96))
    plt.xticks(range(len(list_dep)), list_dep)
    df_ftype_delay.plot(
        kind="line",
        ax=ax,
        marker="x",
        # https://matplotlib.org/stable/gallery/color/named_colors.html
        color={"AVG DEP DELAY": "white", "AVG ARR DELAY": "orange"},
    )

    # Adjusting the metadata
    ax.set_facecolor("black")
    font_prop = get_font_prop("LEDBDREV.TTF")
    # Title
    ax.set_title("TUNISAIR AVERAGE delay", fontproperties=font_prop, y=1.2)
    ax.title.set_fontsize(12)
    ax.title.set_color("orange")

    # legend
    ax.legend(
        loc="best",
        prop=font_prop,
        facecolor="black",
        labelcolor="white",
        edgecolor="black",
        handlelength=0.7,
    )

    # Axies and ticks
    ax.set_xlabel(None)
    ax.set_ylabel("Minutes")

    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(axis="y", colors="white")
    ax.tick_params(axis="x", colors="white")

    # Save figure
    picture_to_save = get_pic_location(current_time, "tunisairperf")
    fig.savefig(picture_to_save, bbox_inches="tight")
    return picture_to_save
