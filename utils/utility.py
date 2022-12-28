#!/usr/bin/python3
import re
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import pytz

TUNISIA_TZ = "Africa/Tunis"


class FontsTunisAlert:
    """_summary_
    to get the font Path
    https://www.1001fonts.com/airport-fonts.html
    """

    def __init__(self):

        self.skyfont = os.path.join(
            os.path.abspath(os.curdir), "fonts/LEDBDREV.TTF")

        self.skyfontInverted = os.path.join(
            os.path.abspath(os.curdir), "fonts/LEDBOARD.TTF")

        self.glyphAirport = os.path.join(
            os.path.abspath(os.curdir), "fonts/GlyphyxOneNF.ttf")


class FileFolderManager:
    """_summary_
    Class for folder and File management
    Reading and writing Json
    Getting file dir
    Reading from txt file
    """

    def __init__(self, directory=None, name_file=None):
        """
        init the directory and file name

        :param directory: (str, optional),name of the directory. defaults to ""
        :param name_file: (str), name of the file must not be empty string. defaults to None
        """

        if directory is None:
            directory = ""

        assert isinstance(directory, str), "directory must be a string"
        assert isinstance(name_file, str), "name_file must be a string"
        assert name_file.strip() != "", "name_file must not be an empty string"

        self.name_file = name_file
        self.dir = directory
        self.local_dir = os.path.join(os.path.abspath(os.curdir), directory)

        if not (Path(self.dir).is_dir()):
            os.mkdir(self.local_dir)

        if name_file:
            self.file_dir = os.path.join(self.local_dir, name_file)
            self.file_exist = Path(self.file_dir).exists()

    def read_txt(self):
        """
        To read .txt file

        :return: None if .txt file empty, else the text of the .txt file
        """

        if not (self.file_exist):
            with open(self.file_dir, "w") as f:
                pass
            print(f"file not found, a new one is created at\n{self.file_dir}")
            return None

        with open(self.file_dir) as f:
            lines = f.readlines()

        return None if len(lines) <= 0 else lines[0]

    def read_json(self, default=None):
        """
        to read the JSON file

        :param default: (dict), default dict to save in JSON file. defaults to None
        :return: either the saved dict in JSON or the default one
        """

        if default is None:
            default = {}
        assert isinstance(
            default, dict), "Wrong Type: default must be a dictionary"

        if not (self.file_exist):
            print(f"file not found, a new one is created at\n{self.file_dir}")
            with open(self.file_dir, "w+") as f:
                json.dump(default, f, indent=4)
            return default
        with open(self.file_dir, "r") as f:
            return json.load(f)

    def save_json(self, dict_f):
        """
        To save the dict in a json file

        :param dict_f: (dict), the dict to save in JSON file
        """
        if dict_f is None:
            dict_f = {}
        assert isinstance(
            dict_f, dict), "Wrong Type: dict_f must be a dictionary"

        with open(self.file_dir, "w+") as f:
            json.dump(dict_f, f, indent=4)


class TimeAttribute:
    """
    class for Date manipulation and date information
    with the adequate Timezone
    """

    def __init__(self, time_str=None):
        """
        To init Type of data

        :param time_str: (str, optional), Type of day format defaults to None
        """

        pytz_tn = pytz.timezone(TUNISIA_TZ)

        self.today = (
            datetime
            .now()
            .astimezone(pytz_tn)
        )

        self.yesterday = (
            (datetime.now() - timedelta(days=1))
            .astimezone(pytz_tn)
        )

        if time_str:
            assert isinstance(
                time_str, str), "Wrong Type: time_str must be a string"

            self.datetime = (
                datetime
                .fromisoformat(time_str)
                .astimezone(pytz_tn)
            )
            self.dateformat = self.datetime.strftime("%d/%m/%Y")
            self.full_hour = self.datetime.strftime("%H:%M")
            self.full_day = self.datetime.strftime("%a %d %b %Y")
            self.hour = self.datetime.strftime("%H")
            self.month = self.datetime.strftime("%m")
            self.full_under_score = self.datetime.strftime("%d_%m_%Y_%H_%M")
            self.short_under_score = self.datetime.strftime("%d_%m_%Y")


def is_blank(myString):
    """_summary_
    to test if the string is blank

    :param myString: (str), string to test

    :returns: (bool), True if blank False if not blank
    """
    if myString is None:
        myString = ""
    assert isinstance(myString, str), "Wrong Type: myString must be a str"

    return not (myString and myString.strip())


def is_not_blank(myString):
    """_summary_
    to test if the string is not blank

    :param myString: (str), string to test

    :returns (bool), True if not blank False if blank
    """
    if myString is None:
        myString = ""
    assert isinstance(myString, str), "Wrong Type: myString must be a str"

    return bool(myString and myString.strip())


def remove_non_alphanumeric(str_to_change):
    """_summary_
    Function to remove all non alphanumerical data

    :param str_to_change: (str), string to clean

    :Returns: (str), string cleaned
    """
    if str_to_change is None:
        str_to_change = ""
    assert isinstance(
        str_to_change, str), "Wrong Type: str_to_change must be a str"

    return re.sub("[^A-Za-z0-9 ]", "", str_to_change)


def get_mins_between(start_date, end_date):
    """_summary_
    function to calculate how many minutes separate start and end

    :param start_date (Datetime): start date
    :param end_date (Datetime): end date

    :returns: (Datetime), minutes between 2 dates
    """
    assert isinstance(
        start_date, datetime), "Wrong Type: start_date must be a datetime"
    assert isinstance(
        end_date, datetime), "Wrong Type: end_date must be a datetime"
    assert end_date > start_date, "Wrong Value: end_date must be later than start_date"

    c = end_date - start_date

    return c.total_seconds() / 60


def get_days_between(start_date, end_date):
    """_summary_
    function to calculate how many days separate start and end

    :param start_date: (Datetime), start date
    :param end_date: (Datetime), end date

    :Returns: (Datetime), number of days in between
    """
    assert isinstance(
        start_date, datetime), "Wrong Type: start_date must be a datetime"
    assert isinstance(
        end_date, datetime), "Wrong Type: end_date must be a datetime"
    assert end_date > start_date, "Wrong Value: end_date must be later than start_date"

    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    c = end_date - start_date

    return c.days


def get_airport_country(airport_iata: str) -> str:
    """_summary_
    Adding Airlines
    from pyairports.airports import Airports
    Code from https://github.com/NICTA/pyairports
    I will handle errors if TUNISAIR made some unknown connections

    Data enrichment
    :param airport_iata: (str), AIRPORT iata code

    :returns: (str), return the airport country
    """

    assert isinstance(
        airport_iata, str), "Wrong Type: airport_iata must be a string"

    from pyairports.airports import Airports

    try:
        return remove_non_alphanumeric(Airports().lookup(airport_iata).country.upper())
    except Exception:
        return "UNKNOWN"


def get_airport_name(airport_iata: str) -> str:
    """_summary_
    Adding Airlines
    from pyairports.airports import Airports
    Code from https://github.com/NICTA/pyairports
    I will handle errors if TUNISAIR made some unknown connections
    Data enrichment

    :param airport_iata: (str), AIRPORT iata code

    :returns: (str), return the airport name
    """
    assert isinstance(
        airport_iata, str), "Wrong Type: airport_iata must be a string"

    from pyairports.airports import Airports

    try:
        return remove_non_alphanumeric(Airports().lookup(airport_iata).name.upper())
    except Exception:
        return "UNKNOWN"


def convert_hex_to_rgb(value: str) -> tuple:
    """_summary_
    https://www.codespeedy.com/create-random-hex-color-code-in-python/
    Function to convert HEX color to RGB

    :param value: (str), the hex code

    :returns: (tuple), the tuple RGB
    """
    assert isinstance(value, str), "Wrong Type: value must be a string"

    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i: i + lv // 3], 16) for i in range(0, lv, lv // 3))
