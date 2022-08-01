#!/usr/bin/python
import re
from datetime import datetime, timezone, timedelta
import sys
import os


def remove_non_alphanumeric(str_to_change):
    """
    Function to remove all non alphanumerical data
    params
    @str_to_change : any string -> str
    """
    return re.sub("[^A-Za-z0-9 ]", "", str_to_change)


def mins_between(start_date, end_date):
    """
    function to get how many minutes is in delay
    params
    @d1 : date in datetime format -> datetime
    @d2 : date in datetime format -> datetime
    """
    c = end_date - start_date
    minutes = c.total_seconds() / 60
    return minutes


def days_between(start_date, end_date):
    """
    To give how many days are between days
    params
    @d1 : date in datetime format -> datetime
    @d2 : date in datetime format -> datetime
    """
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    """
    function to get how many days is between days
    """
    c = end_date - start_date
    days = c.days
    return days


def get_airport_country(airport_iata):
    sys.path.append(os.path.abspath(os.curdir))
    from pyairports.airports import Airports

    """
    # Adding Airlines
    ##################################################
    #f rom pyairports.airports import Airports
    # Code from https://github.com/NICTA/pyairports
    ##################################################
    params
    @airport_iata : the IATA code of the AIRPOT -> str
    """

    """
    # I will handle erros if TUNISAIR made some unknown connections
    # Data enrichment
    # Convert airport_iata to airport full name
    """
    try:
        return remove_non_alphanumeric(
            (Airports().lookup(airport_iata).country).upper()
        )
    except:
        return "UNKNOWN"


def get_airport_name(airport_iata):
    sys.path.append(os.path.abspath(os.curdir))
    from pyairports.airports import Airports

    """
    # Adding Airlines
    ##################################################
    #f rom pyairports.airports import Airports
    # Code from https://github.com/NICTA/pyairports
    ##################################################
    params
    @airport_iata : the IATA code of the AIRPOT -> str
    """

    """
    # I will handle erros if TUNISAIR made some unknown connections
    # Data enrichment
    # Convert airport_iata to airport full name
    """
    try:
        return remove_non_alphanumeric((Airports().lookup(airport_iata).name).upper())
    except:
        return "UNKNOWN"


def hex_to_rgb(value):
    """
    Function to conver HEX color to RGB
    params
    @value the HEX value with # like #F000000 -> str
    """
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))
