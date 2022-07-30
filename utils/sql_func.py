import sqlite3
import os
flight_table_columns = ("ID_FLIGHT", "DEPARTURE_DATE", "FLIGHT_NUMBER", "FLIGHT_STATUS", "DEPARTURE_IATA", "DEPARTURE_AIRPORT",
                        "ARRIVAL_IATA", "ARRIVAL_AIRPORT",  "DEPARTURE_SCHEDULED", "DEPARTUR_HOUR",
                        "ARRIVAL_SCHEDULED", "ARRIVAL_HOUR", "DEPARTURE_ESTIMATED", "ARRIVAL_ESTIMATED", "DEPARTURE_ACTUAL",
                        "ARRIVAL_ACTUAL", "DEPARTURE_DELAY", "ARRIVAL_DELAY")

sql_table_loc = path_flight_type = os.path.join(
    os.path.abspath(os.curdir), 'datasets/SQL table/tunisair_delay.db')


def create_table():
    '''
    Function to create the tunisair_delay database
    '''
    conn = sqlite3.connect(sql_table_loc)
    cursor = conn.cursor()
    sql = '''CREATE TABLE  if not exists "TUNISAIR_FLIGHTS" (
        "ID_FLIGHT" TEXT NOT NULL,
        "DEPARTURE_DATE" TEXT,
        "FLIGHT_NUMBER"	TEXT NOT NULL,
        "FLIGHT_STATUS"	TEXT,
        "DEPARTURE_IATA" TEXT,
        "DEPARTURE_AIRPORT" TEXT,
        "ARRIVAL_IATA" TEXT,
        "ARRIVAL_AIRPORT" TEXT,
        "DEPARTURE_SCHEDULED" TEXT,
        "DEPARTUR_HOUR" INT,
        "ARRIVAL_SCHEDULED" TEXT,
        "ARRIVAL_HOUR" INT,
        "DEPARTURE_ESTIMATED" TEXT,
        "ARRIVAL_ESTIMATED" TEXT,
        "DEPARTURE_ACTUAL" TEXT,
        "ARRIVAL_ACTUAL" TEXT,
        "DEPARTURE_DELAY" INT,
        "ARRIVAL_DELAY" INT,
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
        sql = f"INSERT INTO TUNISAIR_FLIGHTS {str(flight_table_columns)} VALUES {str(values)}"
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
            sql = f'UPDATE TUNISAIR_FLIGHTS SET {cross_col[:-2]} WHERE ID_FLIGHT="{key}"'
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
        sql = f'SELECT 1 FROM TUNISAIR_FLIGHTS WHERE ID_FLIGHT="{key}"'
        check = cursor.execute(sql)
        if check.fetchone() is None:
            conn.commit()
            conn.close()
            return False
        else:
            conn.commit()
            conn.close()
            return True
