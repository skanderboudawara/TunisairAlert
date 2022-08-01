#!/usr/bin/python
import sqlite3
import os
flight_table_columns = ("ID_FLIGHT", "DEPARTURE_DATE", "ARRIVAL_DATE", "FLIGHT_NUMBER", "FLIGHT_STATUS", "DEPARTURE_IATA", "DEPARTURE_AIRPORT",
                        "ARRIVAL_IATA", "ARRIVAL_AIRPORT",  "DEPARTURE_SCHEDULED", "DEPARTURE_HOUR",
                        "ARRIVAL_SCHEDULED", "ARRIVAL_HOUR", "DEPARTURE_ESTIMATED", "ARRIVAL_ESTIMATED", "DEPARTURE_ACTUAL",
                        "ARRIVAL_ACTUAL", "DEPARTURE_DELAY", "ARRIVAL_DELAY", "AIRLINE", "ARRIVAL_COUNTRY", "DEPARTURE_COUNTRY")

sql_table_name = "TUN_FLIGHTS"
sql_table_loc = os.path.join(
    os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')
# Adding Airlines


def create_table():
    '''
    Function to create the tunisair_delay database
    '''
    conn = sqlite3.connect(sql_table_loc)
    cursor = conn.cursor()
    sql = f'''CREATE TABLE  if not exists {sql_table_name} (
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
    )'''
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return True


def insert_in_table(values):
    '''
    Function to insert new item in the SQL Table
    '''
    if create_table():
        conn = sqlite3.connect(sql_table_loc)
        cursor = conn.cursor()
        sql = f"INSERT INTO {sql_table_name} {str(flight_table_columns)} VALUES {str(values)}"
        cursor.execute(sql)
        conn.commit()
        conn.close()


def update_table(key, values):
    '''
    Function to update an item if Table exists & if item exists
    '''
    if create_table():
        if check_key(key):
            print(f'updating {key}')
            cross_col = ''
            for index, col in enumerate(flight_table_columns):
                cross_col = cross_col + col + '="' + str(values[index]) + '", '
            conn = sqlite3.connect(sql_table_loc)
            cursor = conn.cursor()
            sql = f'UPDATE {sql_table_name} SET {cross_col[:-2]} WHERE ID_FLIGHT="{key}"'
            cursor.execute(sql)
            conn.commit()
            conn.close()
        else:
            print(f'Adding {key}')
            insert_in_table(values)


def check_key(key):
    '''
    Function to check if an item exists in a SQL Table
    '''
    if create_table():
        conn = sqlite3.connect(sql_table_loc)
        cursor = conn.cursor()
        sql = f'SELECT 1 FROM {sql_table_name} WHERE ID_FLIGHT="{key}"'
        check = cursor.execute(sql)
        if check.fetchone() is None:
            conn.commit()
            conn.close()
            return False
        else:
            conn.commit()
            conn.close()
            return True


def id_keys():
    '''
    Function to correct or fill an empty new created column
    '''
    if create_table():
        conn = sqlite3.connect(sql_table_loc)
        cursor = conn.cursor()
        sql = f'SELECT ID_FLIGHT FROM {sql_table_name}'
        check = cursor.execute(sql)
        fetch_all = check.fetchall()
        conn.commit()
        conn.close()
        return [key[0] for key in fetch_all]


def modify_column(col_name_input, col_name_output, func):
    '''
    Function to correct or fill an empty new created column
    '''
    if create_table():
        keys = id_keys()
        conn = sqlite3.connect(sql_table_loc)
        cursor = conn.cursor()
        for key in keys:
            input_sql = f'SELECT {col_name_input} FROM {sql_table_name} WHERE ID_FLIGHT="{key}"'
            input = (cursor.execute(input_sql)).fetchone()[0]
            output = func(input)
            output_sql = f'UPDATE {sql_table_name} SET {col_name_output}="{output}" WHERE ID_FLIGHT="{key}"'
            check = cursor.execute(output_sql)
        conn.commit()
        conn.close()
