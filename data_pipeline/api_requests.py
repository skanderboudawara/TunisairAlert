#!/usr/bin/python3
"""
Api AIRLAB request management
"""
import backoff
import requests  # APIs

from data_pipeline.sql_functions import SqlManager  # SQL interactions
from src.utils import FileFolderManager, TimeAttribute, correct_datetime_info, get_airport_country, get_airport_name, get_env, get_flight_key


def fatal_code(error_code):
    """
    Fatal code of response backoff

    :params e: (int), response

    ::returns: (bool), error value response
    """
    return 400 <= error_code.status_code < 500


class AirLabsData(SqlManager):
    """
    A class for managing data related to airlabs.
    Subclass of SqlManager, which is responsible for executing database queries.
    This class also handles file management for json data files of arrival and departure flights.


    :param datetime_query: (datetime), The date and time to query the data for.
    :param force_update: (bool), A flag to indicate whether to force an update of the data. If set to True, the data will be retrieved from the database, even if it already exists in the json files. Default is False.

    :returns: None
    """

    def __init__(self, datetime_query, force_update=None):
        super().__init__()
        if force_update is None:
            force_update = False
        datetime_query = TimeAttribute(datetime_query)
        self.file_arrival = FileFolderManager(
            directory=f"data_pipeline/json_data/arrivals/{datetime_query.month}",
            name_file=f"{datetime_query.short_under_score}_arrival_flights.json",
        )
        self.file_departure = FileFolderManager(
            directory=f"data_pipeline/json_data/departures/{datetime_query.month}",
            name_file=f"{datetime_query.short_under_score}_departure_flights.json",
        )
        self.execute_force_update(force_update)

    def execute_force_update(self, force_update):
        """
        Execute force update for the json files containing arrival and departure flight data.
        If the `force_update` flag is set to True, the data will be retrieved from the API and saved to the json files, even if the data already exists in the files.

        :param force_update: (bool) A flag to indicate whether to force an update of the data. If set to True, the data will be retrieved from the API and saved to the json files.
        :return: None
        """
        if force_update:
            self.file_arrival.save_json(self.get_json_api("departure", "TUN", ["TU", "BJ", "AF", "TO"]).json())
            self.file_departure.save_json(self.get_json_api("arrival", "TUN", ["TU", "BJ", "AF", "TO"]).json())

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_time=300,
        giveup=fatal_code,
    )
    def get_json_api(self, type_flight: str, airport_iata: str, airline_iata=None):
        """
        Retrieve flight data from the API in JSON format.

        :param type_flight: (str) The type of flight to retrieve data for. Can be either "DEPARTURE" or "ARRIVAL".
        :param airport_iata: (str) The IATA code of the airport to retrieve data for.
        :param airline_iata: (list(str), optional) A list of IATA codes of airlines to filter the data by. Default is None.
        :return: (requests.Response) The JSON response of the API request
        """

        _token = get_env("token_airlab")

        assert isinstance(_token, str), "_token must be a string"
        assert _token.strip() != "", "_token must not be an empty string"
        assert isinstance(airport_iata, str), "airport_iata must be a string"
        assert isinstance(type_flight, str), "airport_iata must be a string"
        assert type_flight in {
            "DEPARTURE",
            "ARRIVAL",
        }, "type_flight must be either 'DEPARTURE' or 'ARRIVAL'"
        assert airport_iata.strip() != "", "airport_iata must not be an empty string"

        print("getting json API")
        if airline_iata:
            airline_iata = f"&airline_iata={airline_iata}" if isinstance(airline_iata, str) else "".join([f"&airline_iata={airline}" for airline in airline_iata])

        else:
            airline_iata = ""
        api_request = f"https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata={airport_iata}{airline_iata}&api_key={_token}"
        return requests.get(api_request, timeout=300)

    def get_arrivals(self):
        """
        Retrieve and process arrival flight data.

        :param: None
        :return: None
        """
        json_flight = None
        while not json_flight:
            json_flight = self.file_arrival.read_json()

        self.get_flights(json_flight)

    def get_departures(self):
        """
        Process flight data from the API response.
        Extracts relevant information and performs data cleaning and enrichment.

        :param json_flight: (dict) The JSON flight data from the API response.
        :return: None
        """
        json_flight = None
        while not json_flight:
            json_flight = self.file_departure.read_json()

        self.get_flights(json_flight)

    def get_flights(self, json_flight):
        """
        get the flight regarding the datetime_query and the type of flight

        :param json_flight: (dict), DEPARTURE or ARRIVAL

        :returns: None
        """
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

            # Data enrichment
            departure_airport = get_airport_name(departure_iata)
            arrival_airport = get_airport_name(arrival_iata)
            arrival_country = get_airport_country(arrival_iata)
            departure_country = get_airport_country(departure_iata)

            # Handling if exist
            # Data cleaning
            departure_estimated = flight["dep_estimated"] if "dep_estimated" in flight else ""
            arrival_estimated = flight["arr_estimated"] if "arr_estimated" in flight else ""
            departure_actual = flight["dep_actual"] if "dep_actual" in flight else ""
            arrival_actual = flight["arr_actual"] if "arr_actual" in flight else ""
            departure_delay = flight["delayed"] if "delayed" in flight else 0
            arrival_delay = flight["delayed"] if "delayed" in flight else 0
            departure_delay = 0 if departure_delay is None else int(departure_delay)
            arrival_delay = 0 if arrival_delay is None else int(arrival_delay)

            ##################################################
            # Data Cleaning
            # I have seen that the  flight status and delays are sometimes wrong and needs to be corrected
            # Correction of landing
            # correction of departure delay
            ##################################################

            (dep_hour, departure_date, flight_status, departure_delay,) = correct_datetime_info(
                departure_actual,
                departure_estimated,
                departure_scheduled,
                flight_status,
                departure_delay,
                "active",
            )
            ##################################################
            # Correction of arrival delay
            ##################################################
            (arr_hour, arrival_date, flight_status, arrival_delay,) = correct_datetime_info(
                arrival_actual,
                arrival_estimated,
                arrival_scheduled,
                flight_status,
                arrival_delay,
                "landed",
            )

            ##################################################
            # Data to be injected in the SQL
            # The Flight_number _ FULL DATE will be my unique key
            # Replacing NONE by null text string
            ##################################################
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
            ##################################################
            # Updating the SQL TABLE
            # If the unique key exist => It will be updated
            # Else it will be created
            ##################################################
            self.update_table(flight_key, flight_extracted)
        print("Import completed")
