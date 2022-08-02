#!/usr/bin/python
import os  # OS
from cycler import cycler  # To define color cycle
import matplotlib.pyplot as plt  # plotlib library
from matplotlib import font_manager as fm, markers  # font manager
import pandas as pd  # Pandas library
import matplotlib
from utils.sql_func import execute_sql
from utils.utility import TimeAttribute, FileFolderManager, FontsTunisAlert
from utils.const import SQL_TABLE_NAME

matplotlib.use("Agg")


def get_font_prop(font_name: str, size_font: int):
    """_summary_
    to get the matplotlib font_manager properties
    Args:
        font_name (str): the font name found in FontsTunisAlert class
        size_font (int): the size of the font

    Returns:
        _type_: convert a font path to font_manager properties
    """
    return fm.FontProperties(fname=font_name, size=size_font)


def get_df_sql_data(datetime_query, type_flight: str):
    """_summary_
    to convert a SQL table to a dataframe pandas
    Args:
        datetime_query (_type_): datetime of query
        type_flight (str): DEPARTURE or ARRIVAL

    Returns:
        _type_: a pandas dataframe out of SQL table
    """
    # todays date
    todays_date = TimeAttribute(datetime_query).dateformat
    # Path of the SQL Table
    sql_df = f'SELECT * FROM {SQL_TABLE_NAME} WHERE {type_flight}_DATE="{str(todays_date)}" AND FLIGHT_STATUS<>"cancelled"'
    query = execute_sql(sql_df)
    data = execute_sql(sql_df, "fetchall")
    cols = [column[0] for column in query.description]

    df = pd.DataFrame.from_records(data=data, columns=cols)
    df = df.convert_dtypes()

    return df


def get_pic_location(datetime_query, name="DELAY", type_flight="DEPARTURE"):
    """_summary_
    to retreive where the plot should be stored temporarly
    Args:
        datetime_query (_type_): the date for query
        name (str, optional): the name of file . Defaults to "DELAY".
        type_flight (str, optional): DEPARTURE or ARRIVAL. Defaults to "DEPARTURE".

    Returns:
        _type_: the path location of the temporary save file
    """
    # Check the directory if it exists

    return FileFolderManager(
        dir=f"reports/{TimeAttribute(datetime_query).month}",
        name_file=f"{TimeAttribute(datetime_query).short_under_score}_{type_flight[:3]}_{name}.png",
    ).file_dir


def ax_metadata(ax, title: str, font_prop):
    """_summary_
    To adjust the look of the plots
    Args:
        ax (_type_): the matplotlib plot
        title (str): the title of the plot
        font_prop (_type_): the font properties
    """
    # Adjusting the metadata
    ax.set_facecolor("black")
    # Title

    ax.set_title(
        title,
        fontproperties=font_prop,
        y=1.2,
    )
    ax.title.set_fontsize(12)
    ax.title.set_color("orange")

    # Axies and ticks
    ax.set_xlabel(None)
    ax.set_ylabel("Minutes")

    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(axis="y", colors="white")
    ax.tick_params(axis="x", colors="white")


def plot_from_to_airport(
    datetime_query, type_flight: str, from_airport: str, to_airport: str
):
    """_summary_
    Function to create an SQL request and transform the table into pandas
    the pandas table will be pivoted as function of status and then will be plotted
    in a bar chart
    Args:
        datetime_query (_type_): datetime used for query
        type_flight (str): DEPARTURE or ARRIVAL
        from_airport (str): departure airport
        to_airport (str): arrival airport

    Returns:
        _type_: A bar chart plot with average delay as function of each Airline
        calculated through departure airport to arrival airport
    """
    # Transform the SQL table to pandas + refactor the types
    df = get_df_sql_data(datetime_query, type_flight)
    if df.empty:
        print("DataFrame is empty!")
        return
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
    fig, ax = plt.subplots(facecolor="black", figsize=((1050 / 2) / 96, 160 / 96))

    df_ftype_delay.plot(
        kind="bar",
        alpha=0.7,
        ax=ax,
        # https://matplotlib.org/stable/gallery/color/named_colors.html
        color={
            "TUNISAIR": "#D40100",
            "AIR FRANCE": "white",
            "NOUVELAIR": "#0054A6",
            "TRANSAVIA": "#00D56C",
        },
    )

    font_prop = get_font_prop(FontsTunisAlert().skyfont, 8)
    # legend
    ax.legend(
        fontsize="x-small",
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        ncol=4,
        prop=font_prop,
        facecolor="black",
        labelcolor="white",
        edgecolor="black",
        handlelength=0.7,
        labelspacing=0.3,
        handletextpad=0.6,
    )

    ax_metadata(ax, f"AVERAGE DELAY from {from_airport} -> {to_airport}", font_prop)
    # Save figure
    picture_to_save = get_pic_location(datetime_query, "delayreport", type_flight)
    fig.savefig(picture_to_save, bbox_inches="tight")
    return picture_to_save


def plot_tunisair_arrival_dep_delays(datetime_query):
    """_summary_
    To create a line chart of AVG departure and arrival delays of Tunisair
    Args:
        datetime_query (_type_): datetime used for query

    Returns:
        _type_: a matplotlib plot of the evolution of Tunisair delays for departure
        and arrivals
    """
    # Transform the SQL table to pandas + refactor the types
    df = get_df_sql_data(datetime_query, "DEPARTURE")
    if df.empty:
        print("DataFrame is empty!")
        return
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
    fig, ax = plt.subplots(facecolor="black", figsize=((1150) / 96, 110 / 96))
    plt.xticks(range(len(list_dep)), list_dep)
    df_ftype_delay.plot(
        kind="line",
        ax=ax,
        marker="x",
        # https://matplotlib.org/stable/gallery/color/named_colors.html
        color={"AVG DEP DELAY": "white", "AVG ARR DELAY": "orange"},
    )

    font_prop = get_font_prop(FontsTunisAlert().skyfont, 10)

    # legend
    ax.legend(
        loc="best",
        prop=font_prop,
        facecolor="black",
        labelcolor="white",
        edgecolor="black",
    )

    ax_metadata(ax, f"TUNISAIR AVERAGE delay", font_prop)

    # Save figure
    picture_to_save = get_pic_location(datetime_query, "tunisairperf")
    fig.savefig(picture_to_save, bbox_inches="tight")
    return picture_to_save
