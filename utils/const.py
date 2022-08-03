# !/usr/bin/python3
# CONST
# Import necessary fonts
AIRLINE_NAMES = {
    "TU": "TUNISAIR",
    "AF": "AIR FRANCE",
    "BJ": "NOUVELAIR",
    "HV": "TRANSAVIA",
}
FLIGHT_STATUS = ["scheduled", "cancelled", "active", "landed"]
TYPE_FLIGHTS = ["DEPARTURE", "ARRIVAL"]
SQL_OPERATORS = ["MIN", "MAX", "AVG"]
FONT_SIZE = 20

# SQL Table
SQL_TABLE_NAME = "TUN_FLIGHTS"

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
