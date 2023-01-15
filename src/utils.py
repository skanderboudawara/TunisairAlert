"""
All Modules utilities
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytz
import tweepy
from dotenv import load_dotenv, set_key

from src.airports import AirportNotFoundException, Airports

TUNISIA_TZ = "Africa/Tunis"


def path_dir(sub_path):
    """
    to create an abs path from current dir

    :param sub_path: (str), sub_path in string
    :return: (str), absolute path
    """
    assert isinstance(sub_path, str), "sub_path must be a string"
    return os.path.join(os.path.abspath(os.curdir), sub_path)


SKYFONT = path_dir("src/fonts/LEDBDREV.TTF")
SKYFONT_INVERTED = path_dir("src/fonts/LEDBOARD.TTF")
GLYPH_AIRPORT = path_dir("src/fonts/GlyphyxOneNF.ttf")


def get_env(env_token):
    """
    Get the environment variable from the .env file

    :param env_token: (str) the environment variable to fetch
    :return: (str) the value of the environment variable

    :raises AssertionError: if env_token is not a string or is empty
    :raises AssertionError: if the env_token does not exist or is empty in the .env file
    """
    assert isinstance(env_token, str), "Wrong Type: env_token must be a string"
    assert env_token.strip() != "", "Wrong Value: env_token must not be empty"

    path_env = path_dir(".env")
    if not Path(path_env).exists():
        with open(path_env, "w+", encoding="UTF-8"):
            set_key(
                path_env,
                key_to_set="file_name",
                value_to_set="tunisair_delay.db",
            )
            set_key(
                path_env,
                key_to_set="path",
                value_to_set=path_dir("datasets/SQLtable/"),
            )
            for key in [
                "consumer_key",
                "consumer_secret",
                "access_token",
                "access_token_secret",
                "ip_adress",
                "login",
                "password",
                "token_airlab",
            ]:
                set_key(path_env, key_to_set=key, value_to_set="")

    load_dotenv(path_env)

    assert os.getenv(env_token) is not None, f"Wrong Value: {env_token} do not exist"
    assert os.getenv(env_token).strip() != "", f"Wrong Value: {env_token} must not be empty"

    return os.getenv(env_token)


class FileFolderManager:
    """
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
        self.local_dir = path_dir(directory)

        if not Path(self.dir).is_dir():
            os.mkdir(self.local_dir)

        if name_file:
            self.file_dir = os.path.join(self.local_dir, name_file)
            self.file_exist = Path(self.file_dir).exists()

    def read_json(self, default=None):
        """
        Reads a JSON file and returns its content as a python dictionary.
        If the file does not exist, it creates the file with the provided default dictionary.

        :param default: (dict), default dictionary to save in JSON file if the file does not exist. Defaults to None.
        :return: (dict) the content of the JSON file.
        """

        if default is None:
            default = {}
        assert isinstance(default, dict), "Wrong Type: default must be a dictionary"

        with open(self.file_dir, "r", encoding="UTF-8") as file_json:
            return json.load(file_json)

    def save_json(self, dict_f):
        """
        Save the given dictionary to a JSON file.

        :param dict_f: (dict) The dictionary to be saved in the JSON file.
        :raises TypeError: If the input is not a dictionary.
        """
        if dict_f is None:
            dict_f = {}
        assert isinstance(dict_f, dict), "Wrong Type: dict_f must be a dictionary"

        with open(self.file_dir, "w+", encoding="UTF-8") as file_json:
            json.dump(dict_f, file_json, indent=4)


class TimeAttribute:
    """
    class for manipulating and extracting date and time information,
    with the appropriate timezone.

    :param time_str: (str, optional) the time in string format, defaults to None.
    """

    def __init__(self, time_str=None):
        """
        Initialize the class and set the timezone.

        :param time_str: (str, optional) the time in string format, defaults to None.
        """

        self.pytz_tn = pytz.timezone(TUNISIA_TZ)

        self.today = datetime.now().astimezone(self.pytz_tn)

        self.yesterday = (datetime.now() - timedelta(days=1)).astimezone(self.pytz_tn)

        if time_str:
            assert isinstance(time_str, (str, datetime)), "Wrong Type: time_str must be a string or datetime"
            if isinstance(time_str, str):
                self.datetime = datetime.fromisoformat(time_str).astimezone(self.pytz_tn)
            else:
                self.datetime = time_str.astimezone(self.pytz_tn)
            self.dateformat = self.datetime.strftime("%d/%m/%Y")
            self.full_hour = self.datetime.strftime("%H:%M")
            self.full_day = self.datetime.strftime("%a %d %b %Y")
            self.hour = self.datetime.strftime("%H")
            self.month = self.datetime.strftime("%m")
            self.full_under_score = self.datetime.strftime("%d_%m_%Y_%H_%M")
            self.short_under_score = self.datetime.strftime("%d_%m_%Y")

    def get_mins_between(self, end_date):
        """
        Calculate the number of minutes between two dates.

        :param end_date: (datetime) The end date as a datetime object
        :returns: (float) Number of minutes between the start and end date
        :raises: AssertionError if start_date is not a datetime, end_date is not a datetime, end_date is earlier than start_date
        """

        assert isinstance(self.datetime, datetime), "Wrong Type: start_date must be a datetime"
        assert isinstance(end_date, datetime), "Wrong Type: end_date must be a datetime"
        assert end_date.astimezone(None) >= self.datetime.astimezone(None), "Wrong Value: end_date must be later than start_date"
        time_in_sec = end_date.astimezone(None) - self.datetime.astimezone(None)
        return time_in_sec.total_seconds() / 60

    def get_days_between(self, end_date):
        """
        function to calculate how many days separate start and end

        :param start_date: (datetime), start date
        :param end_date: (datetime), end date
        :raises AssertionError: if start_date is not a datetime, end_date is not a datetime or end_date is earlier than start_date.
        :returns: (int), number of days in between
        """

        assert isinstance(self.datetime, datetime), "Wrong Type: start_date must be a datetime"
        assert isinstance(end_date, datetime), "Wrong Type: end_date must be a datetime"
        end_date = end_date.astimezone(self.pytz_tn)
        assert end_date.astimezone(None) >= self.datetime.astimezone(None), "Wrong Value: end_date must be later than start_date"
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        time_in_sec = end_date.astimezone(None) - self.datetime.astimezone(None)
        return time_in_sec.days + 1


def is_blank(my_string):
    """
    Check if a given string is blank. A string is considered blank if it is empty or contains only whitespace characters.

    :param my_string: (str) The string to check for blankness.
    :return: (bool) True if the string is blank, False otherwise.
    """
    my_string = str(my_string)

    return not (my_string and my_string.strip())


def remove_non_alphanumeric(str_to_change):
    """
    Function to remove all non alphanumerical data

    :param str_to_change: (str), string to clean

    ::returns: (str), string cleaned
    """
    if str_to_change is None:
        str_to_change = ""
    assert isinstance(str_to_change, str), "Wrong Type: str_to_change must be a str"

    return re.sub("[^A-Za-z0-9 ]", "", str_to_change)


def get_airport_country(airport_iata: str) -> str:
    """
    Adding Airlines
    from src.airports import Airports
    Code from https://github.com/NICTA/pyairports
    I will handle errors if TUNISAIR made some unknown connections

    Data enrichment

    :param airport_iata: (str), AIRPORT iata code
    :returns: (str), return the airport country
    """

    assert isinstance(airport_iata, str), "Wrong Type: airport_iata must be a string"

    try:
        return remove_non_alphanumeric(Airports().lookup(airport_iata).country.upper())
    except AirportNotFoundException:
        return "UNKNOWN"


def get_airport_name(airport_iata: str) -> str:
    """
    Adding Airlines
    from src.airports import Airports
    Code from https://github.com/NICTA/pyairports
    I will handle errors if TUNISAIR made some unknown connections
    Data enrichment

    :param airport_iata: (str), AIRPORT iata code

    ::returns: (str), return the airport name
    """
    assert isinstance(airport_iata, str), "Wrong Type: airport_iata must be a string"

    try:
        return remove_non_alphanumeric(Airports().lookup(airport_iata).name.upper())
    except AirportNotFoundException:
        return "UNKNOWN"


def convert_hex_to_rgb(value: str) -> tuple:
    """
    https://www.codespeedy.com/create-random-hex-color-code-in-python/
    Function to convert HEX color to RGB

    :param value: (str), the hex code

    ::returns: (tuple), the tuple RGB
    """
    assert isinstance(value, str), "Wrong Type: value must be a string"

    value = value.lstrip("#")
    hexa_value = len(value)
    return tuple(int(value[i : i + hexa_value // 3], 16) for i in range(0, hexa_value, hexa_value // 3))


def correct_datetime_info(
    datetime_actual: str,
    datetime_estimated: str,
    datetime_scheduled: str,
    flight_status: str,
    datetime_delay: int,
    text: str,
):
    """
    To correct the dates depending on the data

    :param datetime_actual: (str), actual datetime time
    :param datetime_estimated: (str), estimated datetime time
    :param datetime_scheduled: (str), scheduled datetime time
    :param flight_status: (str), 'scheduled', 'cancelled', 'active', 'landed'
    :param datetime_delay: (str), datetime delays
    :param text: (str), the text to put once datetime is compared to actual date

    :returns: (tuple), (datetime_hour, real_datetime, actual_flight_status, real_delay)
    """

    assert isinstance(datetime_actual, str), "Wrong Type datetime_actual must be a str"
    assert isinstance(datetime_estimated, str), "Wrong Type datetime_estimated must be a str"
    assert isinstance(datetime_scheduled, str), "Wrong Type datetime_scheduled must be a str"
    assert isinstance(flight_status, str), "Wrong Type flight_status must be a str"
    assert isinstance(datetime_delay, int), "Wrong Type datetime_delay must be an int "
    assert isinstance(text, str), "Wrong Type text must be a str"

    datetime_datetime_scheduled = TimeAttribute(datetime_scheduled)
    today_datetime = datetime_datetime_scheduled.today
    effective_date = datetime_datetime_scheduled
    datetime_delay = 0 if is_blank(datetime_delay) else datetime_delay
    for date_check in [datetime_estimated, datetime_actual]:
        if not is_blank(date_check):
            effective_date = TimeAttribute(date_check)
    if effective_date.datetime > datetime_datetime_scheduled.datetime:
        datetime_delay = datetime_datetime_scheduled.get_mins_between(effective_date.datetime)
    if (today_datetime > effective_date.datetime) & (flight_status != "cancelled"):
        flight_status = text
    return (
        f"{effective_date.hour}h",
        effective_date.dateformat,
        flight_status,
        datetime_delay,
    )


def get_flight_key(flight_number: str, departure_scheduled: str) -> str:
    """
    To generate the flight key from flight_number & departure_scheduled

    :param flight_number: (str), the flight number
    :param departure_scheduled: (str), the departure scheduled

    :returns: (str), the SQL unique ID key
    """
    departure_scheduled = TimeAttribute(departure_scheduled)
    return f"{flight_number}_{departure_scheduled.full_under_score}"


def post_tweet_with_pic(tweet_msg, picture_loc=None):
    """
    To post a tweet with a picture or not.

    :param tweet_msg: (str), The tweet message to be posted
    :param picture_loc: (str), the path of the picture. Default is None
    :returns: None
    """

    auth = tweepy.OAuthHandler(
        consumer_key=get_env("consumer_key"),
        consumer_secret=get_env("consumer_secret"),
        access_token=get_env("access_token"),
        access_token_secret=get_env("access_token_secret"),
    )

    api = tweepy.API(auth)

    # Upload image
    if picture_loc is not None:
        media = api.media_upload(picture_loc)
        api.update_status(status=tweet_msg, media_ids=[media.media_id])
    else:
        api.update_status(status=tweet_msg)
