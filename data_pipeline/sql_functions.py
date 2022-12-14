#!/usr/bin/python3
"""
Module to manage the SQL queries
"""
import ftplib
import sqlite3
import time

from src.const import DEFAULT_TABLE, FLIGHT_TABLE_COLUMNS, SQL_TABLE_NAME
from src.utils import (
    FileFolderManager,
    TimeAttribute,
    correct_datetime_info,
    get_env,
)


class SqlManager:
    """
    SQL Manager class
    """

    def __init__(self):
        self.filename = get_env("file_name")
        self.path_sql_db = FileFolderManager(
            directory="data_pipeline/", name_file=self.filename
        ).file_dir
        self.execution = self.execute_sql(
            f"""
            CREATE TABLE  if not exists {SQL_TABLE_NAME}
            {DEFAULT_TABLE}
            """
        )

    def execute_sql(self, sql=None, fetchmethod=None):
        """
        Function to execute and SQL and return
        - The query
        - Or Fetchone
        - or FetchAll

        :param sql (str): the SQL code
        :param fetchmethod (str, optional): the fetch method. Defaults to None.

        :returns: (list) the query or the fetch
        """
        conn = sqlite3.connect(self.path_sql_db)
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

    def insert_in_table(self, values: tuple):
        """
        Function to insert new item in the SQL Table

        :parm: values (tuple): a tuple of all values to be inserted

        :returns: None
        """
        self.execute_sql(
            f"""
            INSERT INTO {SQL_TABLE_NAME}
            {str(FLIGHT_TABLE_COLUMNS)} VALUES {values}
            """
        )

    def update_table(self, key: str, values: tuple):
        """
        Function to update an item if Table exists & if item exists

        :parm key (str): is the key id
        :parm values (tuple): a tuple of all the values to be updated

        :returns: None
        """
        if self.check_key(key):
            cross_col = ""
            for index, col in enumerate(FLIGHT_TABLE_COLUMNS):
                cross_col = cross_col + col + '="' + str(values[index]) + '", '
            self.execute_sql(
                f"""
                UPDATE {SQL_TABLE_NAME}
                SET {cross_col[:-2]}
                WHERE ID_FLIGHT="{key}"
                """
            )
        else:
            self.insert_in_table(values)

    def check_key(self, key: str):
        """
        Function to check if an item exists in a SQL Table

        :param key (str): the id key

        :returns: (bool), return true or false if key found
        """
        check = self.execute_sql(
            f"""
            SELECT 1
            FROM {SQL_TABLE_NAME}
            WHERE (ID_FLIGHT = "{key}")
            """,
            "fetchone",
        )

        return check is not None

    def id_keys(self, condition=""):
        """
        Function to correct or fill an empty new created column

        :param condition (str, optional): to create a condition of Where if needed. Defaults to "".

        :returns: (list), list of all Key (meeting condition optional)
        """
        fetch_all = self.execute_sql(
            f"""
            SELECT ID_FLIGHT
            FROM {SQL_TABLE_NAME}
            {condition}
            """,
            "fetchall",
        )

        return [key[0] for key in fetch_all]

    def modify_column(self, col_name_input: str, col_name_output: str, func):
        """
        Function to correct or fill an empty new created column

        :param col_name_input (str):  the column to extract information from
        :param col_name_output (str): the column to modify
        :param func (function): a function that will be applied on @col_name_input and outputted in @col_name_output

        :returns: None
        """
        keys = self.id_keys()
        for key in keys:
            values = self.execute_sql(
                f"""
                SELECT {col_name_input}
                FROM {SQL_TABLE_NAME}
                WHERE (ID_FLIGHT = "{key}")
                """,
                "fetchone",
            )[0]
            output = func(values)
            self.execute_sql(
                f'UPDATE {SQL_TABLE_NAME} SET {col_name_output}="{output}" WHERE ID_FLIGHT="{key}"'
            )

    def clean_sql_table(self, datetime_query):
        """
        Function to clean SQL table and re adjust all the time information
        dep_hour, departure_date, flight_status, departure_delay
        arr_hour, arrival_date, flight_status, arrival_delay

        :param datetime_query (str): datetime of query

        :returns: None
        """

        time.sleep(1)
        query_date = TimeAttribute(datetime_query).dateformat
        keys = self.id_keys(f'WHERE (DEPARTURE_DATE = "{query_date}")')
        pragma = self.execute_sql(
            f"PRAGMA table_info({SQL_TABLE_NAME})", "fetchall"
        )
        cols = [column[1] for column in pragma]

        def column_index(col_name):
            """
            get Column name and return its position

            :param col_name (str): column name

            :returns: (int), the int position
            """
            return cols.index(col_name)

        for key in keys:
            values = list(
                self.execute_sql(
                    f"""
                    SELECT *
                    FROM {SQL_TABLE_NAME}
                    WHERE (ID_FLIGHT = "{key}")
                    """,
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

            self.update_table(key, values)

        print("cleaning completed")
        time.sleep(1)

    def import_ftp_sqldb(self):
        """
        To pull the SQL Table from the FTP servera
        Credentials are saved in /credentials/ftp.json
        """
        path = get_env("path")
        ftp = ftplib.FTP(get_env("ip_adress"))
        ftp.login(get_env("login"), get_env("password"))
        ftp.cwd(path)
        ftp.retrbinary(
            f"RETR {self.filename}", open(self.path_sql_db, "wb").write
        )
        ftp.quit()

        print("FTP DB imported")
