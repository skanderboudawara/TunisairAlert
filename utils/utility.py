#!/usr/bin/python
import re
import sys
import os
import json


class FontsTunisAlert:
    def __init__(self):
        self.skyfont = os.path.join(os.path.abspath(os.curdir), "fonts/LEDBDREV.TTF")
        self.skyfontInverted = os.path.join(
            os.path.abspath(os.curdir), "fonts/LEDBOARD.TTF"
        )
        self.glyphAirport = os.path.join(
            os.path.abspath(os.curdir), "fonts/GlyphyxOneNF.ttf"
        )


class FileFolderManager:
    def __init__(self, dir="", name_file=None):
        self.name_file = name_file
        self.dir = dir
        self.local_dir = os.path.join(os.path.abspath(os.curdir), dir)

        if not (os.path.isdir(self.local_dir)):
            os.mkdir(self.local_dir)

        if name_file:
            self.file_dir = os.path.join(self.local_dir, name_file)
            self.file_exist = os.path.exists(self.file_dir)

    def read_txt(self):
        if self.file_exist:
            with open(self.file_dir) as f:
                lines = f.readlines()
            if len(lines) <= 0:
                return None
            return lines[0]
        else:
            with open(self.file_dir, "w") as f:
                pass
            print(f"file not found, a new one is created at\n{self.file_dir}")
            return None

    def read_json(self, default={}):
        if self.file_exist:
            with open(self.file_dir) as f:
                return json.load(f)
        else:
            print(f"file not found, a new one is created at\n{self.file_dir}")
            with open(self.file_dir, "w") as f:
                json.dump(default, f, indent=4)
            return default

    def save_json(self, dict):
        with open(self.file_dir, "w") as f:
            json.dump(dict, f, indent=4)


class TimeAttribute:
    def __init__(self, time_str=None):
        from datetime import datetime, timedelta
        import pytz

        TUNISIA_TZ = "Africa/Tunis"

        self.today = datetime.now().astimezone(pytz.timezone(TUNISIA_TZ))
        self.yesterday = (datetime.now() - timedelta(days=1)).astimezone(
            pytz.timezone(TUNISIA_TZ)
        )
        if time_str:
            self.datetime = datetime.fromisoformat(str(time_str)).astimezone(
                pytz.timezone(TUNISIA_TZ)
            )
            self.dateformat = self.datetime.strftime("%d/%m/%Y")
            self.hour = self.datetime.strftime("%H")
            self.month = self.datetime.strftime("%m")
            self.full_under_score = self.datetime.strftime("%d_%m_%Y_%H_%M")
            self.short_under_score = self.datetime.strftime("%d_%m_%Y")


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
