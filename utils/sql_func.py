#!/usr/bin/python
from utils.utility import get_airport_name, FileFolderManager, TimeAttribute
from utils.const import FLIGHT_TABLE_COLUMNS, SQL_TABLE_NAME
import sys
import sqlite3
import time
import os
import sys
import os


PATH_SQL_DB = FileFolderManager(
    dir="datasets/SQL table", name_file="tunisair_delay.db"
).file_dir

# Adding Airlines


def execute_sql(sql, fetchmethod=None):
    """_summary_
    Function to execute and SQL and return
    - The query
    - Or Fetchone
    - or FetchAll
    Args:
        sql (_type_): the SQL code
        fetchmethod (_type_, optional): the fetch method. Defaults to None.

    Returns:
        _type_: the query or the fetch
    """
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
    """_summary_
    Function to create the tunisair_delay database
    Returns:
        _type_: True if the table exist or have been created
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


def insert_in_table(values: tuple):
    """_summary_
    Function to insert new item in the SQL Table
    Args:
        values (tuple): a tuple of all values to be inserted
    """
    if create_table():
        execute_sql(
            f"INSERT INTO {SQL_TABLE_NAME} {str(FLIGHT_TABLE_COLUMNS)} VALUES {values}")


def update_table(key: str, values: tuple):
    """_summary_
    Function to update an item if Table exists & if item exists

    Args:
        key (str): is the key id
        values (tuple): a tuple of all the values to be updated
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


def check_key(key: str):
    """_summary_
    Function to check if an item exists in a SQL Table

    Args:
        key (str): the id key

    Returns:
        _type_: return true or false if key found
    """
    if create_table():
        check = execute_sql(
            f'SELECT 1 FROM {SQL_TABLE_NAME} WHERE ID_FLIGHT="{key}"', "fetchone")

        return check is not None


def id_keys(condition=""):
    """_summary_
    Function to correct or fill an empty new created column
    Args:
        condition (str, optional): to create a condition of Where if needed. Defaults to "".

    Returns:
        _type_: list of all Key (meeting condition optional)
    """
    if create_table():
        fetch_all = execute_sql(
            f"SELECT ID_FLIGHT FROM {SQL_TABLE_NAME} {condition}", "fetchall"
        )
        return [key[0] for key in fetch_all]


def modify_column(col_name_input: str, col_name_output: str, func):
    """_summary_
    Function to correct or fill an empty new created column

    Args:
        col_name_input (str):  the column to extract information from
        col_name_output (str): the column to modify
        func (_type_): a function that will be applied on @col_name_input and outputted in @col_name_output
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
    """_summary_
    Function to clean SQL table and re adjust all the time information
    dep_hour, departure_date, flight_status, departure_delay
    arr_hour, arrival_date, flight_status, arrival_delay
    Args:
        datetime_query (_type_): datetime of query
    """
    sys.path.append(os.path.abspath(os.curdir))
    from utils.airlabs_imports import correct_datetime_info

    time.sleep(1)
    query_date = TimeAttribute(datetime_query).dateformat
    if create_table():

        keys = id_keys(f'WHERE DEPARTURE_DATE="{query_date}"')
        pragma = execute_sql(
            f"PRAGMA table_info({SQL_TABLE_NAME})", "fetchall")
        cols = [column[1] for column in pragma]

        def column_index(col_name):
            """_summary_
            get Column name and return its position
            Args:
                col_name (_type_): column name

            Returns:
                _type_: the int position
            """
            return cols.index(col_name)

        for key in keys:
            values = list(
                execute_sql(
                    f'SELECT * FROM {SQL_TABLE_NAME} WHERE ID_FLIGHT="{key}"',
                    "fetchone",
                )
            )
            key = values[column_index("ID_FLIGHT")]

            # datetime_actual, datetime_estimated, datetime_scheduled, flight_status, datetime_delay, text
            # dep_hour, departure_date, flight_status, departure_delay
            (
                values[column_index("DEPARTURE_HOUR")],
                values[column_index("DEPARTURE_DATE")],
                values[column_index("FLIGHT_STATUS")],
                values[column_index("DEPARTURE_DELAY")],
            ) = correct_datetime_info(
                datetime_actual=values[column_index("DEPARTURE_ACTUAL")],
                datetime_estimated=values[column_index("DEPARTURE_ESTIMATED")],
                datetime_scheduled=values[column_index("DEPARTURE_SCHEDULED")],
                flight_status=values[column_index("FLIGHT_STATUS")],
                datetime_delay=values[column_index("DEPARTURE_DELAY")],
                text="active",
            )

            # arr_hour, arrival_date, flight_status, arrival_delay
            (
                values[column_index("ARRIVAL_HOUR")],
                values[column_index("ARRIVAL_DATE")],
                values[column_index("FLIGHT_STATUS")],
                values[column_index("ARRIVAL_DELAY")],
            ) = correct_datetime_info(
                datetime_actual=values[column_index("ARRIVAL_ACTUAL")],
                datetime_estimated=values[column_index("ARRIVAL_ESTIMATED")],
                datetime_scheduled=values[column_index("ARRIVAL_SCHEDULED")],
                flight_status=values[column_index("FLIGHT_STATUS")],
                datetime_delay=values[column_index("ARRIVAL_DELAY")],
                text="landed",
            )
            values = tuple(values)

            update_table(key, values)

    print("cleaning completed")
    time.sleep(1)
