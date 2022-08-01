#!/usr/bin/python
from utils.utility import get_airport_name
import sys
import sqlite3
import time
import os
import sys
import os


FLIGHT_TABLE_COLUMNS = (
    "ID_FLIGHT",
    "DEPARTURE_DATE",
    "ARRIVAL_DATE",
    "FLIGHT_NUMBER",
    "FLIGHT_STATUS",
    "DEPARTURE_IATA",
    "DEPARTURE_AIRPORT",
    "ARRIVAL_IATA",
    "ARRIVAL_AIRPORT",
    "DEPARTURE_SCHEDULED",
    "DEPARTURE_HOUR",
    "ARRIVAL_SCHEDULED",
    "ARRIVAL_HOUR",
    "DEPARTURE_ESTIMATED",
    "ARRIVAL_ESTIMATED",
    "DEPARTURE_ACTUAL",
    "ARRIVAL_ACTUAL",
    "DEPARTURE_DELAY",
    "ARRIVAL_DELAY",
    "AIRLINE",
    "ARRIVAL_COUNTRY",
    "DEPARTURE_COUNTRY",
)

SQL_TABLE_NAME = "TUN_FLIGHTS"
PATH_SQL_DB = os.path.join(
    os.path.abspath(os.curdir), "datasets/SQL table/tunisair_delay.db"
)
# Adding Airlines


def execute_sql(sql, fetchmethod=None):
    conn = sqlite3.connect(PATH_SQL_DB)
    cursor = conn.cursor()
    sql_execute = cursor.execute(sql)
    fetch_sql = sql_execute
    if fetchmethod == "fetchone":
        fetch_sql = sql_execute.fetchone()
    elif fetchmethod == "fetchall":
        fetch_sql = sql_execute.fetchall()
    conn.commit()
    conn.close()
    return fetch_sql


def create_table():
    """
    Function to create the tunisair_delay database
    """
    execute_sql(
        f"""CREATE TABLE  if not exists {SQL_TABLE_NAME} (
        "ID_FLIGHT" TEXT NOT NULL,
        "DEPARTURE_DATE" TEXT,
        "ARRIVAL_DATE" TEXT,
        "FLIGHT_NUMBER"	TEXT NOT NULL,
        "FLIGHT_STATUS"	TEXT,
        "DEPARTURE_IATA" TEXT,
        "DEPARTURE_AIRPORT" TEXT,
        "ARRIVAL_IATA" TEXT,
        "ARRIVAL_AIRPORT" TEXT,
        "DEPARTURE_SCHEDULED" TEXT,
        "DEPARTURE_HOUR" INT,
        "ARRIVAL_SCHEDULED" TEXT,
        "ARRIVAL_HOUR" INT,
        "DEPARTURE_ESTIMATED" TEXT,
        "ARRIVAL_ESTIMATED" TEXT,
        "DEPARTURE_ACTUAL" TEXT,
        "ARRIVAL_ACTUAL" TEXT,
        "DEPARTURE_DELAY" INT,
        "ARRIVAL_DELAY" INT,
        "AIRLINE" TEXT,
        "ARRIVAl_COUNTRY" TEXT,
        "DEPARTURE_COUNTRY" TEXT,
        PRIMARY KEY("ID_FLIGHT")
    )"""
    )

    return True


def insert_in_table(values):
    """
    Function to insert new item in the SQL Table
    params
    @values : a tuple of all values to be inserted -> tuple
    """
    if create_table():
        execute_sql(
            f"INSERT INTO {SQL_TABLE_NAME} {str(FLIGHT_TABLE_COLUMNS)} VALUES {str(values)}"
        )


def update_table(key, values):
    """
    Function to update an item if Table exists & if item exists
    params
    @key is the key id -> str
    @values : a tuple of all the values to be updated -> tuple
    """
    if create_table():
        if check_key(key):
            cross_col = ""
            for index, col in enumerate(FLIGHT_TABLE_COLUMNS):
                cross_col = cross_col + col + '="' + str(values[index]) + '", '
            execute_sql(
                f'UPDATE {SQL_TABLE_NAME} SET {cross_col[:-2]} WHERE ID_FLIGHT="{key}"'
            )
        else:
            insert_in_table(values)


def check_key(key):
    """
    Function to check if an item exists in a SQL Table
    params
    @key : the id key -> str
    """
    if create_table():
        check = execute_sql(
            f'SELECT 1 FROM {SQL_TABLE_NAME} WHERE ID_FLIGHT="{key}"', "fetchone"
        )
        return False if check is None else True


def id_keys(condition=""):
    """
    Function to correct or fill an empty new created column
    """
    if create_table():
        fetch_all = execute_sql(
            f"SELECT ID_FLIGHT FROM {SQL_TABLE_NAME} {condition}", "fetchall"
        )
        return [key[0] for key in fetch_all]


def modify_column(col_name_input, col_name_output, func):
    """
    Function to correct or fill an empty new created column
    params
    @col_name_input : the column to extract information from -> str
    @col_name_output : the column to modify -> str
    @func : a function that will be applied on @col_name_input and outputed in @col_name_output -> function
    """
    if create_table():
        keys = id_keys()
        for key in keys:
            values = execute_sql(
                f'SELECT {col_name_input} FROM {SQL_TABLE_NAME} WHERE ID_FLIGHT="{key}"',
                "fetchone",
            )[0]
            output = func(values)
            execute_sql(
                f'UPDATE {SQL_TABLE_NAME} SET {col_name_output}="{output}" WHERE ID_FLIGHT="{key}"'
            )


def clean_sql_table(datetime_query):
    sys.path.append(os.path.abspath(os.curdir))
    from utils.airlabs_imports import correct_datetime_info

    time.sleep(1)
    query_date = datetime_query.strftime("%d/%m/%Y")
    if create_table():

        keys = id_keys(f'WHERE DEPARTURE_DATE="{query_date}"')

        for key in keys:
            values = list(
                execute_sql(
                    f'SELECT * FROM {SQL_TABLE_NAME} WHERE ID_FLIGHT="{key}"',
                    "fetchone",
                )
            )
            key = values[0]

            # datetime_actual, datetime_estimated, datetime_scheduled, flight_status, datetime_delay, text
            # dep_hour, departure_date, flight_status, departure_delay
            values[10], values[1], values[4], values[17] = correct_datetime_info(
                datetime_actual=values[15],
                datetime_estimated=values[13],
                datetime_scheduled=values[9],
                flight_status=values[4],
                datetime_delay=values[17],
                text="active",
            )

            # arr_hour, arrival_date, flight_status, arrival_delay

            values[12], values[2], values[4], values[18] = correct_datetime_info(
                datetime_actual=values[16],
                datetime_estimated=values[14],
                datetime_scheduled=values[11],
                flight_status=values[4],
                datetime_delay=values[18],
                text="landed",
            )
            values = tuple(values)

            update_table(key, values)

    print("cleaning completed")
    time.sleep(1)


sys.path.append(os.path.abspath(os.curdir))

modify_column("DEPARTURE_IATA", "DEPARTURE_AIRPORT", get_airport_name)
modify_column("ARRIVAL_IATA", "ARRIVAL_AIRPORT", get_airport_name)
