#!/usr/bin/python
import requests  # APIs
from utils.utility import (
    mins_between,
    get_airport_country,
    get_airport_name,
    TimeAttribute,
    isNotBlank,
    isBlank,
    FileFolderManager,
)
from utils.sql_func import update_table  # SQL interactions
import backoff


def get_token():
    """
    To retreive the token from the token.txt file
    # https://airlabs.co
    """
    return FileFolderManager(dir="credentials", name_file="token.txt").read_txt()


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
def get_json_api(type_flight: str, airport_iata: str, airline_iata=None):
    """
    To make the API Request
    params
    @type_flight : DEPARTURE or ARRIVAL -> STR
    @airport_iata : IATA code of airport -> STR
    @airline_iata : LIST of airline IATA codes (List of strings) -> LIST
    """
    _token = get_token()
    if isBlank(_token):
        print("No token")
        return

    if isBlank(airport_iata):
        print("IATA airport is mandatory")
        return

    print("getting json API")
    if airline_iata:
        airline_iata = (
            "&airline_iata=" + airline_iata
            if isinstance(airline_iata, str)
            else "".join(["&airline_iata=" + airline for airline in airline_iata])
        )
    else:
        airline_iata = ""
    api_request = f"https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata={airport_iata}{airline_iata}&api_key={_token}"
    print(api_request)
    return requests.get(api_request)


def json_folder_and_name(type_flight: str, datetime_query):
    """
    To get the json file location
    params
    @type_flight : DEPARTURE or ARRIVAL -> STR
    @datetime_query : current datetime -> datetime
    """
    directory_flight_type = (
        f"datasets/{type_flight}/{TimeAttribute(datetime_query).month}"
    )

    file_flight_type = (
        f"{TimeAttribute(datetime_query).short_under_score}_{type_flight}_flights.json"
    )
    return directory_flight_type, file_flight_type


def get_json_dict(datetime_query, force_upade: bool, type_flight: str):
    """
    Return JSON dictionnary
    params
    @json_file : location of the json file -> str
    @force_update : to force calling the API request -> Boolean
    @type_flight : DEPARTURE or ARRIVAL -> str
    """

    directory_flight_type, file_flight_type = json_folder_and_name(
        type_flight, datetime_query
    )

    if force_upade:
        effective_airlines = ["TU", "BJ", "AF", "TO"]
        response = get_json_api(type_flight, "TUN", effective_airlines)
        json_flight = response.json()
        FileFolderManager(
            dir=directory_flight_type, name_file=file_flight_type
        ).save_json(dict=json_flight)
        return json_flight
    else:
        json_flight = FileFolderManager(
            dir=directory_flight_type, name_file=file_flight_type
        ).read_json()
        if (
            (json_flight != {})
            & (json_flight is not None)
            & ("response" in json_flight)
        ):
            return json_flight
        else:
            return False


def correct_datetime_info(
    datetime_actual: str,
    datetime_estimated: str,
    datetime_scheduled: str,
    flight_status: str,
    datetime_delay: int,
    text: str,
) -> tuple:
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
    today_datetime = TimeAttribute().today
    datetime_datetime_scheduled = TimeAttribute(datetime_scheduled).datetime
    effective_date = datetime_datetime_scheduled
    flight_status = flight_status
    datetime_delay = datetime_delay if isNotBlank(datetime_delay) else 0

    for date_check in [datetime_estimated, datetime_actual]:
        if isNotBlank(date_check):
            effective_date = TimeAttribute(date_check).datetime

    dat_hour = TimeAttribute(effective_date).hour
    effective_date_str = TimeAttribute(effective_date).dateformat

    if effective_date > datetime_datetime_scheduled:
        datetime_delay = mins_between(datetime_datetime_scheduled, effective_date)
    if (today_datetime > effective_date) & (flight_status != "cancelled"):
        flight_status = text
    return dat_hour + "h", effective_date_str, flight_status, datetime_delay


def get_flight_key(flight_number: str, departure_scheduled: str) -> str:
    """
    To generate the flight key from flight_number & departure_scheduled
    """
    return f"{flight_number}_{TimeAttribute(departure_scheduled).full_under_score}"


def get_flights(type_flight: str, datetime_query, force_upade=False):
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
    # datetime_query = (datetime.now()- timedelta(days=1)).astimezone(pytz.timezone(TUNISIA_TZ)) # To be used for yesterday

    json_flight = get_json_dict(datetime_query, force_upade, type_flight)
    if not (json_flight):
        print("JSON file is corrupted")
        return
    # Get the response data
    real_time_flights = json_flight["response"]

    # Loop through each flight and  prepare the data
    for flight in real_time_flights:
        airline = flight["airline_iata"]
        flight_number = flight["flight_iata"]
        flight_status = flight["status"]
        departure_iata = flight["dep_iata"]
        arrival_iata = flight["arr_iata"]
        departure_scheduled = flight["dep_time"]
        arrival_scheduled = flight["arr_time"]
        """
        # Data enrichment
        """
        departure_airport = get_airport_name(departure_iata)
        arrival_airport = get_airport_name(arrival_iata)
        arrival_country = get_airport_country(arrival_iata)
        departure_country = get_airport_country(departure_iata)
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
        departure_delay = 0 if departure_delay is None else int(departure_delay)
        arrival_delay = 0 if arrival_delay is None else int(arrival_delay)
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
        (arr_hour, arrival_date, flight_status, arrival_delay,) = correct_datetime_info(
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
            departure_iata,
            departure_airport,
            arrival_iata,
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
