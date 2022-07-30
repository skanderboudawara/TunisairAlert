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
