#!/usr/bin/python3
"""
Module to manage the SQL queries
"""
import ftplib
import sqlite3
import time

from src.const import DEFAULT_TABLE, FLIGHT_TABLE_COLUMNS, SQL_TABLE_NAME
from src.utils import FileFolderManager, TimeAttribute, correct_datetime_info, get_env


class SqlManager:
    """
    SQL Manager class
    """

    def __init__(self):
        self.filename = get_env("file_name")
        self.path_sql_db = FileFolderManager(directory="data_pipeline/", name_file=self.filename).file_dir
        self.execution = self.execute_sql(
            f"""
            CREATE TABLE  if not exists {SQL_TABLE_NAME}
            {DEFAULT_TABLE}
            """
        )

    def execute_sql(self, sql=None, fetchmethod=None):
        """
        Execute an SQL query and return the results.

        :param sql: (str) The SQL query to be executed.
        :param fetchmethod: (str, optional) The method to use to retrieve the results. Can be "fetchone" or "fetchall". Default is None, which returns the query object.
        :return: (list) The query results.
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
        Insert a new item into the SQL table.

        :param values: (tuple) A tuple of values to be inserted into the table.
        :return: None
        """
        self.execute_sql(
            f"""
            INSERT INTO {SQL_TABLE_NAME}
            {str(FLIGHT_TABLE_COLUMNS)} VALUES {values}
            """
        )

    def update_table(self, key: str, values: tuple):
        """
        Update an item in the SQL table.
        If the item does not exist, it will be inserted instead.

        :param key: (str) The key (ID) of the item to be updated.
        :param values: (tuple) A tuple of values to update the item with.
        :return: None
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
        Check if an item with the given key exists in the SQL table.

        :param key: (str) The key (ID) of the item to check for.
        :return: (bool) True if the key exists in the table, False otherwise.
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
        Retrieve a list of all keys (ID) in the SQL table, with an optional condition.

        :param condition: (str, optional) An optional SQL WHERE clause to filter the keys by. Default is an empty string.
        :return: (list) A list of all keys that meet the given condition.
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
        Modify the values of a column by applying a function to the values of another column.

        :param col_name_input: (str) The name of the column to extract values from.
        :param col_name_output: (str) The name of the column to modify.
        :param func: (function) A function to apply on the values of col_name_input and output in col_name_output.
        :return: None
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
            self.execute_sql(f'UPDATE {SQL_TABLE_NAME} SET {col_name_output}="{output}" WHERE ID_FLIGHT="{key}"')

    def clean_sql_table(self, datetime_query):
        """
        Function to clean SQL table and re adjust all the time information
        dep_hour, departure_date, flight_status, departure_delay
        arr_hour, arrival_date, flight_status, arrival_delay

        :param datetime_query: (str) datetime of query

        :returns: None
        """

        time.sleep(1)
        query_date = TimeAttribute(datetime_query).dateformat
        keys = self.id_keys(f'WHERE (DEPARTURE_DATE = "{query_date}")')
        pragma = self.execute_sql(f"PRAGMA table_info({SQL_TABLE_NAME})", "fetchall")
        cols = [column[1] for column in pragma]

        def column_index(col_name):
            """
            Get the index of a column in a table

            :param col_name: (str) the name of the column
            :return: (int) the index of the column in the table
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
            (values[column_index("DEPARTURE_HOUR")], values[column_index("DEPARTURE_DATE")], values[column_index("FLIGHT_STATUS")], values[column_index("DEPARTURE_DELAY")],) = correct_datetime_info(
                datetime_actual=values[column_index("DEPARTURE_ACTUAL")],
                datetime_estimated=values[column_index("DEPARTURE_ESTIMATED")],
                datetime_scheduled=values[column_index("DEPARTURE_SCHEDULED")],
                flight_status=values[column_index("FLIGHT_STATUS")],
                datetime_delay=values[column_index("DEPARTURE_DELAY")],
                text="active",
            )

            # arr_hour, arrival_date, flight_status, arrival_delay
            (values[column_index("ARRIVAL_HOUR")], values[column_index("ARRIVAL_DATE")], values[column_index("FLIGHT_STATUS")], values[column_index("ARRIVAL_DELAY")],) = correct_datetime_info(
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
        This method connects to the FTP server using the credentials saved in the credentials/ftp.json file.
        It then changes the working directory to the specified path, retrieves the SQLite database file with the specified filename, and writes it to the specified path on the local machine.

        :param: None

        :returns: None
        """
        path = get_env("path")
        ftp = ftplib.FTP(get_env("ip_adress"))
        ftp.login(get_env("login"), get_env("password"))
        ftp.cwd(path)
        ftp.retrbinary(f"RETR {self.filename}", open(self.path_sql_db, "wb").write)
        ftp.quit()

        print("FTP DB imported")
