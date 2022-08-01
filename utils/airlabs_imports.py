#!/usr/bin/python
import requests  # APIs
import os  # Create and organize folders
import json  # Json manipulations
from datetime import datetime  # datetime
import pytz  # timezone
from utils.utility import (
    mins_between,
    days_between,
    get_airport_country,
    get_airport_name,
)
from utils.sql_func import update_table  # SQL interactions
import backoff


##################################################
# Global variables
##################################################
tz = "Africa/Tunis"
# https://airlabs.co


def get_token():
    """
    To retreive the token from the token.txt file
    """
    if not (os.path.exists(os.path.join(os.path.abspath(os.curdir), "token.txt"))):
        with open(os.path.join(os.path.abspath(os.curdir), "token.txt"), "w") as f:
            pass

    with open(os.path.join(os.path.abspath(os.curdir), "token.txt")) as f:
        lines = f.readlines()
        if len(lines) <= 0:
            print(
                "You need to register to airlabs.co and put the token in the token.txt file"
            )
            return False
        _token = lines[0]
    if (_token == "") | (_token is None):
        print(
            "You need to register to airlabs.co and put the token in the token.txt file"
        )
        return False
    else:
        return _token


def fatal_code(e):
    """
    Fatal code of response backoff
    params
    @e : error value response
    """
    return 400 <= e.response.status_code < 500


@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_time=300, giveup=fatal_code
)
def get_json_api(type_flight, airport_iata, airline_iata=None):
    """
    To make the API Request
    params
    @type_flight : DEPARTURE or ARRIVAL -> STR
    @airport_iata : IATA code of airport -> STR
    @airline_iata : LIST of airline IATA codes (List of strings) -> LIST
    """
    _token = get_token()
    if _token:
        print("getting json API")
        if airline_iata is not None:
            airline_iata = (
                "&airline_iata=" + airline_iata
                if isinstance(airline_iata, str)
                else "".join(["&airline_iata=" + airline for airline in airline_iata])
            )
        api_request = f"https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata={airport_iata}{airline_iata}&api_key={_token}"
        print(api_request)
        return requests.get(api_request)


def json_location(type_flight, datetime_query):
    """
    To get the json file location
    params
    @type_flight : DEPARTURE or ARRIVAL -> STR
    @datetime_query : current datetime -> datetime
    """
    directory_flight_type = f'datasets/{type_flight}/{datetime_query.strftime("%m")}'
    path_flight_type = os.path.join(
        os.path.abspath(os.curdir), directory_flight_type)
    if not (os.path.isdir(path_flight_type)):
        os.mkdir(path_flight_type)

    file_flight_type = (
        f'{datetime_query.strftime("%d-%m-%Y")}_{type_flight}_flights.json'
    )
    return f"{path_flight_type}/{file_flight_type}"


def correct_datetime_info(
    datetime_actual,
    datetime_estimated,
    datetime_scheduled,
    flight_status,
    datetime_delay,
    text,
):
    """
    Function to correct arrival information
    params:
    @datetime_query : current time in datetime -> datetime
    @arrival_actual : actual arrival time -> str
    @arrival_estimated : estiated arrival time -> str
    @arrival_scheduled : scheduled arrival time -> str
    @flight_status : 'scheduled', 'cancelled', 'active', 'landed' -> str
    @arrival_delay : arrival delay -> int

    output
    @arr_hour -> str
    @arrival_date -> str
    @flight_status -> str
    @arrival_delay -> int
    """
    today_datetime = datetime.now().astimezone(pytz.timezone(tz))
    datetime_datetime_scheduled = datetime.fromisoformat(datetime_scheduled).astimezone(
        pytz.timezone(tz)
    )
    effective_date = datetime_datetime_scheduled
    flight_status = flight_status
    datetime_delay = (
        datetime_delay if (datetime_delay is not None) & (
            datetime_delay != "") else 0
    )

    for date_check in [datetime_estimated, datetime_actual]:
        if (date_check != "") & (date_check is not None):
            effective_date = datetime.fromisoformat(date_check).astimezone(
                pytz.timezone(tz)
            )

    dat_hour = effective_date.strftime("%H")
    effective_date_str = effective_date.strftime("%d/%m/%Y")

    if effective_date > datetime_datetime_scheduled:
        datetime_delay = mins_between(
            datetime_datetime_scheduled, effective_date)
    if (today_datetime > effective_date) & (flight_status != "cancelled"):
        flight_status = text
    return dat_hour + "h", effective_date_str, flight_status, datetime_delay


def get_flight_key(flight_number, departure_scheduled):
    datetime_departure_scheduled = datetime.fromisoformat(
        departure_scheduled
    ).astimezone(pytz.timezone(tz))
    return flight_number + "_" + datetime_departure_scheduled.strftime("%d_%m_%Y_%H_%M")


def get_json_dict(json_file, force_upade, type_flight):
    """
    Return JSON dictionnary
    params
    @json_file : location of the json file -> str
    @force_update : to force calling the API request -> Boolean
    @type_flight : DEPARTURE or ARRIVAL -> str
    """
    if os.path.isfile(json_file) & ~(force_upade):
        print("opening file...")
        with open(json_file) as f:
            json_flight = json.load(f)
    # Else pull request
    else:
        tunisian_airprorts = ["TUN", "NBE", "DJE",
                              "MIR", "SFA", "TOE", "GAF", "GAE"]
        effective_airlines = ["TU", "BJ", "AF", "HV"]
        response = get_json_api(type_flight, "TUN", effective_airlines)
        json_flight = response.json()
        if json_flight:
            with open(json_file, "w") as f:
                json.dump(response.json(), f, indent=4)
    return json_flight


def get_flight(type_flight, datetime_query, force_upade=False):
    """
    if type_flight = 'departure' then the function will execute the departure function informaton
    else if type_flight = 'arrival' then the function will execute the arrival function information

    The aim of this function is to pull request from Airlabs API the information needed on Tunisair
    To correct the delay timing
    To store the information on SQL Tables

    Since I'm subscribed to a free plan I'm limited to 1000 request per month
    That's why I am saving the files in JSON files.

    The main goal is to have 1 file / day / Month
    params
    @type_flight : DEPARTURE or ARRIVAL -> str
    @force_update : to force calling the API or not by default it's false -> Boolean
    """
    # datetime_query = (datetime.now()- timedelta(days=1)).astimezone(pytz.timezone(tz)) # To be used for yesterday

    json_file = json_location(type_flight, datetime_query)
    json_flight = get_json_dict(json_file, force_upade, type_flight)

    if (json_flight == {}) | (not ("response" in json_flight)) | (json_flight is None):
        print(
            "You need to register to airlabs.co and put the token in the token.txt file"
        )
        print(
            "be careful you may have reached your limit free plan Airlabs API requests"
        )
        return

    # Get the response data
    real_time_flights = json_flight["response"]

    # Loop through each flight and  prepare the data
    for flight in real_time_flights:
        airline = flight["airline_iata"]
        flight_number = flight["flight_iata"]
        flight_status = flight["status"]
        departure_IATA = flight["dep_iata"]
        arrival_IATA = flight["arr_iata"]
        departure_scheduled = flight["dep_time"]
        arrival_scheduled = flight["arr_time"]
        """
        # Data enrichment
        """
        departure_airport = get_airport_name(departure_IATA)
        arrival_airport = get_airport_name(arrival_IATA)
        arrival_country = get_airport_country(arrival_IATA)
        departure_country = get_airport_country(departure_IATA)
        """
        # Handling if exist
        # Data cleaning
        """
        departure_estimated = (
            flight["dep_estimated"] if "dep_estimated" in flight else ""
        )
        arrival_estimated = flight["arr_estimated"] if "arr_estimated" in flight else ""
        departure_actual = flight["dep_actual"] if "dep_actual" in flight else ""
        arrival_actual = flight["arr_actual"] if "arr_actual" in flight else ""
        departure_delay = flight["delayed"] if "delayed" in flight else 0
        arrival_delay = flight["delayed"] if "delayed" in flight else 0

        """
        ##################################################
        # Data Cleaning
        # I have seen that the  flight status and delays are sometimes wrong and needs to be corrected
        # Correction of landing
        # correction of departure delay
        ##################################################
        """

        (
            dep_hour,
            departure_date,
            flight_status,
            departure_delay,
        ) = correct_datetime_info(
            departure_actual,
            departure_estimated,
            departure_scheduled,
            flight_status,
            departure_delay,
            "active",
        )
        """
        ##################################################
        # Correction of arrival delay
        ##################################################
        """
        arr_hour, arrival_date, flight_status, arrival_delay = correct_datetime_info(
            arrival_actual,
            arrival_estimated,
            arrival_scheduled,
            flight_status,
            arrival_delay,
            "landed",
        )

        """
        ##################################################
        # Data to be injected in the SQL
        # The Flight_number _ FULL DATE will be my unique key
        # Replacing NONE by null text string
        ##################################################
        """
        flight_key = get_flight_key(flight_number, departure_scheduled)
        flight_extracted = (
            flight_key,
            departure_date,
            arrival_date,
            flight_number,
            flight_status,
            departure_IATA,
            departure_airport,
            arrival_IATA,
            arrival_airport,
            departure_scheduled,
            dep_hour,
            arrival_scheduled,
            arr_hour,
            departure_estimated,
            arrival_estimated,
            departure_actual,
            arrival_actual,
            departure_delay,
            arrival_delay,
            airline,
            arrival_country,
            departure_country,
        )
        """
        ##################################################
        # Updating the SQL TABLE
        # If the unique key exist => It will be updated
        # Else it will be created
        ##################################################
        # """
        update_table(flight_key, flight_extracted)
    print("Import completed")
