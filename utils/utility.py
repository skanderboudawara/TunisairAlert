#!/usr/bin/python
import re
from datetime import datetime, timezone, timedelta


def remove_nonAlpha(str_to_change):
    '''
    Function to remove all non alphanumerical data
    '''
    return re.sub('[^A-Za-z0-9]', ' ', str_to_change)


def mins_between(d1, d2):
    '''
    function to get how many minutes is in delay
    '''
    c = d2 - d1
    minutes = c.total_seconds() / 60
    return abs(minutes)


def days_between(d1, d2):
    d1 = d1.replace(hour=0, minute=0, second=0, microsecond=0)
    d2 = d2.replace(hour=0, minute=0, second=0, microsecond=0)
    '''
    function to get how many days is between days
    '''
    c = d1 - d2
    days = c.days
    return days


def time_compare_message(time_in_between):
    '''
    Function to return a message in function of
    time_between
    the on and estimated
    '''
    time_compare = ''
    if (time_in_between == 0):
        time_compare = 'on time'
    else:
        time_compare = f'late by {str(time_in_between)} minutes'

    return time_compare


def get_airport_country(airport_iata):
    # Adding Airlines
    ##################################################
    #f rom pyairports.airports import Airports
    # Code from https://github.com/NICTA/pyairports
    ##################################################
    import sys
    import os
    sys.path.append(os.path.abspath(os.curdir))
    from pyairports.airports import Airports
    # I will handle erros if TUNISAIR made some unknown connections
    # Data enrichment
    # Convert airport_iata to airport full name
    try:
        return (Airports().lookup(airport_iata).country).upper()
    except:
        return 'UNKNOWN'


def get_airport_name(airport_iata):
    # Adding Airlines
    ##################################################
    #f rom pyairports.airports import Airports
    # Code from https://github.com/NICTA/pyairports
    ##################################################
    import sys
    import os
    sys.path.append(os.path.abspath(os.curdir))
    from pyairports.airports import Airports
    # I will handle erros if TUNISAIR made some unknown connections
    # Data enrichment
    # Convert airport_iata to airport full name
    try:
        return Airports().lookup(airport_iata).city + ' ' + Airports().lookup(airport_iata).name
    except:
        return 'UNKNOWN'
