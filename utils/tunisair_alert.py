#!/usr/bin/python
import requests  # APIs
import os  # Create and organize folders
import json  # Json manipulations
from datetime import datetime  # datetime
import pytz  # timezone
from utils.utility import mins_between, days_between, get_airport_country, get_airport_name
from utils.sql_func import update_table  # SQL interactions
import backoff


##################################################
# Global variables
##################################################
tz = "Africa/Tunis"
# https://airlabs.co


def get_token():
    '''
    To retreive the token from the token.txt file
    '''
    if not(os.path.exists(os.path.join(os.path.abspath(os.curdir), 'token.txt'))):
        with open(os.path.join(os.path.abspath(os.curdir), 'token.txt'), 'w') as f:
            pass

    with open(os.path.join(os.path.abspath(os.curdir), 'token.txt')) as f:
        lines = f.readlines()
        if (len(lines) <= 0):
            print(
                'You need to register to airlabs.co and put the token in the token.txt file')
            return False
        _token = lines[0]
    if (_token == '') | (_token is None):
        print('You need to register to airlabs.co and put the token in the token.txt file')
        return False
    else:
        return _token


def fatal_code(e):
    '''
    Fatal code of response backoff
    '''
    return 400 <= e.response.status_code < 500


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_time=300,
                      giveup=fatal_code)
def get_json_api(type_flight, airport_iata, airline_iata=None):
    '''
    To make the API Request
    '''
    _token = get_token()
    if _token:
        print('getting json API')
        if airline_iata is not None:
            airline_iata = '&airline_iata='+airline_iata if isinstance(
                airline_iata, str) else ''.join(['&airline_iata='+airline for airline in airline_iata])
        api_request = f'https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata={airport_iata}{airline_iata}&api_key={_token}'
        print(api_request)
        return requests.get(api_request)


def json_location(type_flight, current_time):
    '''
    To get the json file location 
    '''
    directory_flight_type = f'datasets/{type_flight}/{current_time.strftime("%m")}'
    path_flight_type = os.path.join(
        os.path.abspath(os.curdir), directory_flight_type)
    if not (os.path.isdir(path_flight_type)):
        os.mkdir(path_flight_type)

    file_flight_type = f'{current_time.strftime("%d-%m-%Y")}_{type_flight}_flights.json'
    return f'{path_flight_type}/{file_flight_type}'


def correct_arrival_info(current_time, arrival_actual, arrival_estimated, arrival_scheduled, flight_status, arrival_delay):
    '''
    Function to correct arrival information
    arr_hour
    arrival_date
    flight_status
    arrival_delay
    '''
    datetime_arrival_scheduled = datetime.fromisoformat(
        arrival_scheduled).astimezone(pytz.timezone(tz))
    arr_hour = datetime_arrival_scheduled.strftime("%H")
    arrival_date = datetime_arrival_scheduled.strftime("%d/%m/%Y")
    flight_status = flight_status
    arrival_delay = arrival_delay if arrival_delay is not None else 0
    if (arrival_actual != '') & (arrival_actual is not None):
        datime_arrival_actual = datetime.fromisoformat(
            arrival_actual).astimezone(pytz.timezone(tz))
        arr_hour = datime_arrival_actual.strftime("%H")
        arrival_date = datime_arrival_actual.strftime("%d/%m/%Y")
        if datime_arrival_actual <= current_time:
            flight_status = 'landed'
            arrival_delay = mins_between(
                datime_arrival_actual, datetime_arrival_scheduled)
        if days_between(datime_arrival_actual, datetime_arrival_scheduled) != 0:
            flight_status = 'cancelled'
    elif (arrival_estimated != '') & (arrival_estimated is not None):
        datetime_arrival_estimated = datetime.fromisoformat(
            arrival_estimated).astimezone(pytz.timezone(tz))
        arr_hour = datetime_arrival_estimated.strftime("%H")
        arrival_date = datetime_arrival_estimated.strftime("%d/%m/%Y")
        if datetime_arrival_estimated <= current_time:
            flight_status = 'landed'
            arrival_delay = mins_between(
                datetime_arrival_estimated, datetime_arrival_scheduled)
        if days_between(datetime_arrival_estimated, datetime_arrival_scheduled) != 0:
            flight_status = 'cancelled'
    elif (arrival_scheduled != '') & (arrival_scheduled is not None):
        if datetime_arrival_scheduled <= current_time:
            flight_status = 'landed'
    return arr_hour+'h', arrival_date, flight_status, arrival_delay


def correct_departure_info(departure_actual, departure_estimated, departure_scheduled, flight_status, departure_delay):
    '''
    Function to correct departure information
    dep_hour 
    departure_date
    flight_status
    departure_delay
    '''
    datetime_departure_scheduled = datetime.fromisoformat(
        departure_scheduled).astimezone(pytz.timezone(tz))
    dep_hour = datetime_departure_scheduled.strftime("%H")
    departure_date = datetime_departure_scheduled.strftime("%d/%m/%Y")
    departure_delay = departure_delay if departure_delay is not None else 0
    flight_status = flight_status

    if (departure_actual != '') & (departure_actual is not None):
        datetime_departure_actual = datetime.fromisoformat(
            departure_actual).astimezone(pytz.timezone(tz))
        dep_hour = datetime_departure_actual.strftime("%H")
        departure_date = datetime_departure_actual.strftime("%d/%m/%Y")
        if datetime_departure_actual > datetime_departure_scheduled:
            departure_delay = mins_between(
                datetime_departure_actual, datetime_departure_scheduled)
        if days_between(datetime_departure_actual, datetime_departure_scheduled) != 0:
            flight_status = 'cancelled'
    elif (departure_estimated != '') & (departure_estimated is not None):
        datetime_departure_estimated = datetime.fromisoformat(
            departure_estimated).astimezone(pytz.timezone(tz))
        dep_hour = datetime_departure_estimated.strftime("%H")
        departure_date = datetime_departure_estimated.strftime("%d/%m/%Y")
        if datetime_departure_estimated > datetime_departure_scheduled:
            departure_delay = mins_between(
                datetime_departure_estimated, datetime_departure_scheduled)
        if days_between(datetime_departure_estimated, datetime_departure_scheduled) != 0:
            flight_status = 'cancelled'
    return dep_hour+'h', departure_date, flight_status, departure_delay


def get_flight_key(flight_number, departure_scheduled):
    datetime_departure_scheduled = datetime.fromisoformat(
        departure_scheduled).astimezone(pytz.timezone(tz))
    return flight_number + '_' + datetime_departure_scheduled.strftime("%d_%m_%Y_%H_%M")


def get_json_dict(json_file, force_upade, type_flight):
    '''
    Return JSON dictionnary
    '''
    if os.path.isfile(json_file) & ~(force_upade):
        print('opening file...')
        with open(json_file) as f:
            json_flight = json.load(f)
    # Else pull request
    else:
        tunisian_airprorts = ['TUN', 'NBE', 'DJE',
                              'MIR', 'SFA', 'TOE', 'GAF', 'GAE']
        effective_airlines = ['TU', 'BJ', 'AF', 'HV']
        response = get_json_api(type_flight, 'TUN', effective_airlines)
        json_flight = response.json()
        if json_flight:
            with open(json_file, 'w') as f:
                json.dump(response.json(), f, indent=4)
    return json_flight


def get_flight(type_flight, force_upade=False):
    '''
    if type_flight = 'departure' then the function will execute the departure function informaton
    else if type_flight = 'arrival' then the function will execute the arrival function information
    
    The aim of this function is to pull request from Airlabs API the information needed on Tunisair
    To correct the delay timing
    To store the information on SQL Tables

    Since I'm subscribed to a free plan I'm limited to 1000 request per month 
    That's why I am saving the files in JSON files. 

    The main goal is to have 1 file / day / Month 
    '''
    # To get Airlabs token stored in token.txt

    # File and dir checking
    # current_time = (datetime.now()- timedelta(days=1)).astimezone(pytz.timezone(tz)) # To be used for yesterday
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    json_file = json_location(type_flight, current_time)
    json_flight = get_json_dict(json_file, force_upade, type_flight)

    if (json_flight == {}) | (not('response' in json_flight)) | (json_flight is None):
        print('You need to register to airlabs.co and put the token in the token.txt file')
        print('be careful you may have reached your limit free plan Airlabs API requests')
        return

    # Get the response data
    real_time_flights = json_flight['response']

    # Loop through each flight and  prepare the data
    for flight in real_time_flights:
        airline = flight['airline_iata']
        flight_number = flight['flight_iata']
        flight_status = flight['status']
        departure_IATA = flight['dep_iata']
        arrival_IATA = flight['arr_iata']
        departure_scheduled = flight['dep_time']
        arrival_scheduled = flight['arr_time']
        # Data enrichment
        departure_airport = get_airport_name(departure_IATA)
        arrival_airport = get_airport_name(arrival_IATA)
        arrival_country = get_airport_country(arrival_IATA)
        departure_country = get_airport_country(departure_IATA)

        # Handling if exist
        # Data cleaning
        departure_estimated = flight['dep_estimated'] if 'dep_estimated' in flight else ''
        arrival_estimated = flight['arr_estimated'] if 'arr_estimated' in flight else ''
        departure_actual = flight['dep_actual'] if 'dep_actual' in flight else ''
        arrival_actual = flight['arr_actual'] if 'arr_actual' in flight else ''
        departure_delay = flight['delayed'] if 'delayed' in flight else 0
        arrival_delay = flight['delayed'] if 'delayed' in flight else 0

        ##################################################
        # Data Cleaning
        # I have seen that the  flight status and delays are sometimes wrong and needs to be corrected
        # Correction of landing
        # Correction of arrival delay
        ##################################################
        arr_hour, arrival_date, flight_status, arrival_delay = correct_arrival_info(
            current_time, arrival_actual, arrival_estimated, arrival_scheduled, flight_status, arrival_delay)
        ##################################################
        # correction of departure delay
        ##################################################
        dep_hour, departure_date, flight_status, departure_delay = correct_departure_info(
            departure_actual, departure_estimated, departure_scheduled, flight_status, departure_delay)

        ##################################################
        # Data to be injected in the SQL
        # The Flight_number _ FULL DATE will be my unique key
        # Replacing NONE by null text string
        ##################################################
        flight_key = get_flight_key(flight_number, departure_scheduled)
        flight_extracted = (flight_key, departure_date, arrival_date, flight_number,
                            flight_status, departure_IATA, departure_airport, arrival_IATA, arrival_airport,
                            departure_scheduled, dep_hour, arrival_scheduled, arr_hour,
                            departure_estimated, arrival_estimated, departure_actual,
                            arrival_actual, departure_delay, arrival_delay, airline,
                            arrival_country, departure_country)
        ##################################################
        # Updating the SQL TABLE
        # If the unique key exist => It will be updated
        # Else it will be created
        ##################################################
        update_table(flight_key, flight_extracted)
