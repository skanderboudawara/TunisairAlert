#!/usr/bin/python3

from src.utils import get_airport_country, get_airport_name, TimeAttribute, FileFolderManager, get_env, correct_datetime_info, get_flight_key
from src.sql_func import SqlManager  # SQL interactions

import backoff
import requests  # APIs


def fatal_code(e):
    """
    Fatal code of response backoff

    :params e: (int), response

    ::returns: (bool), error value response
    """
    return 400 <= e.response.status_code < 500


class AirLabsData(SqlManager):
    def __init__(self, datetime_query, force_update=None):
        super().__init__()
        if force_update is None:
            force_update = False
        datetime_query = TimeAttribute(datetime_query)
        self.file_arrival = FileFolderManager(directory=f"datasets/arrival/{datetime_query.month}", name_file=f"{datetime_query.short_under_score}_arrival_flights.json")
        self.file_departure = FileFolderManager(directory=f"datasets/departure/{datetime_query.month}", name_file=f"{datetime_query.short_under_score}_departure_flights.json")
        self.execute_force_update(force_update)
        
    
    def execute_force_update(self, force_update):
        """
        to save api response

        :param force_update: (bool), True will force the update
        
        :returns: none
        """
        if force_update:
            self.file_arrival.save_json(self.get_json_api("departure", "TUN", ["TU", "BJ", "AF", "TO"]).json())
            self.file_departure.save_json(self.get_json_api("arrival", "TUN", ["TU", "BJ", "AF", "TO"]).json())
    
    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_time=300, giveup=fatal_code)
    def get_json_api(self, type_flight: str, airport_iata: str, airline_iata=None):
        """
        To make the API Request

        :param type_flight: (str), DEPARTURE or ARRIVAL
        :param airport_iata: (str), IATA code of airport
        :param airline_iata: (list(str), optional), LIST of airline IATA codes (List of strings). Defaults to None.

        :returns: (dict), the JSON pulled from the API
        """
        _token = get_env("token_airlab")
        assert isinstance(_token, str), "_token must be a string"
        assert _token.strip() != "", "_token must not be an empty string"
        assert isinstance(airport_iata, str), "airport_iata must be a string"
        assert airport_iata.strip() != "", "airport_iata must not be an empty string"

        print("getting json API")
        if airline_iata:
            airline_iata = (
                f"&airline_iata={airline_iata}"
                if isinstance(airline_iata, str)
                else "".join([f"&airline_iata={airline}" for airline in airline_iata])
            )

        else:
            airline_iata = ""
        api_request = f"https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata={airport_iata}{airline_iata}&api_key={_token}"
        return requests.get(api_request)
    
    def get_arrivals(self):
        """
        Will get the arrival
        
        :param: None
        
        :return: None
        """
        json_flight = None
        while not json_flight:
            json_flight = self.file_arrival.read_json()
            
        self.get_flights(json_flight)
        
    def get_departures(self):
        """
        Will get the depatures
        
        :param: None
        
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

            (dep_hour, departure_date, flight_status, departure_delay) = correct_datetime_info(departure_actual, departure_estimated, departure_scheduled, flight_status, departure_delay, "active")
            ##################################################
            # Correction of arrival delay
            ##################################################
            (arr_hour, arrival_date, flight_status, arrival_delay,) = correct_datetime_info(arrival_actual, arrival_estimated, arrival_scheduled, flight_status, arrival_delay, "landed")

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









