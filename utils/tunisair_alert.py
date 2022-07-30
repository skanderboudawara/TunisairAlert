import requests  # APIs
import os  # Create and organize folders
import json  # Json manipulations
from datetime import datetime, timedelta  # datetime
import pytz  # timezone
from utils.utility import mins_between
from utils.sql_func import update_table  # SQL interactions


##################################################
#f rom pyairports.airports import Airports
# Code from https://github.com/NICTA/pyairports
##################################################
from pyairports.airports import Airports

##################################################
# Global variables
##################################################
tz = "Africa/Tunis"
# https://airlabs.co

# To get Airlabs token stored in token.txt
with open('token.txt') as f:
    _token = f.readlines()[0]


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

    # File and dir checking
    # current_time = (datetime.now()- timedelta(days=1)).astimezone(pytz.timezone(tz)) # To be used for yesterday
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    directory_flight_type = f'datasets/{type_flight}/{current_time.strftime("%m")}'
    path_flight_type = os.path.join(
        os.path.abspath(os.curdir), directory_flight_type)
    if not (os.path.isdir(path_flight_type)):
        os.mkdir(path_flight_type)
    file_flight_type = f'{current_time.strftime("%d-%m-%Y")}_{type_flight}_flights.json'

    # If JSON file exist use it
    if os.path.isfile(f'{path_flight_type}/{file_flight_type}') & ~(force_upade):
        print('opening file...')
        with open(f'{path_flight_type}/{file_flight_type}') as f:
            json_flight = json.load(f)

    # Else pull request
    else:
        print('getting json API')
        response = requests.get(
            f'https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata=TUN&{type_flight[:3]}_time={current_time.strftime("%d-%m-%Y")}airline_iata=TU&api_key={_token}')
        if response.json():
            with open(f'{path_flight_type}/{file_flight_type}', 'w') as f:
                json.dump(response.json(), f)
            json_flight = response.json()

    if json_flight == {}:
        return

    # Get the response data
    real_time_flights = json_flight['response']

    # Loop through each flight and  prepare the data
    for flight in real_time_flights:
        flight_number = flight['flight_iata']
        flight_status = flight['status']
        departure_IATA = flight['dep_iata']
        arrival_IATA = flight['arr_iata']
        departure_airport = Airports().lookup(departure_IATA).city + ' ' + \
            Airports().lookup(departure_IATA).name
        arrival_airport = Airports().lookup(arrival_IATA).city + ' ' + \
            Airports().lookup(arrival_IATA).name

        departure_scheduled = flight['dep_time']
        arrival_scheduled = flight['arr_time']
        dep_hour = datetime.fromisoformat(departure_scheduled).astimezone(
            pytz.timezone(tz)).strftime("%H")
        arr_hour = datetime.fromisoformat(arrival_scheduled).astimezone(
            pytz.timezone(tz)).strftime("%H")
        departure_estimated = flight['dep_estimated'] if 'dep_estimated' in flight else None
        arrival_estimated = flight['arr_estimated'] if 'arr_estimated' in flight else None
        departure_actual = flight['dep_actual'] if 'dep_actual' in flight else None
        arrival_actual = flight['arr_actual'] if 'arr_actual' in flight else None
        departure_delay = flight['delayed'] if 'delayed' in flight else 0
        arrival_delay = flight['delayed'] if 'delayed' in flight else 0
        departure_date = datetime.fromisoformat(departure_scheduled).astimezone(
            pytz.timezone(tz)).strftime("%d/%m/%Y")

        ##################################################
        # I have seen that the  flight status and delays are sometimes wrong and needs to be corrected
        # Correction of landing
        # Correction of arrival delay
        ##################################################
        if arrival_actual is not None:
            arr_hour = datetime.fromisoformat(arrival_actual).astimezone(
                pytz.timezone(tz)).strftime("%H")
            if datetime.fromisoformat(arrival_actual).astimezone(pytz.timezone(tz)) <= current_time:
                flight_status = 'landed'
                arrival_delay = mins_between(
                    datetime.fromisoformat(
                        arrival_actual).astimezone(pytz.timezone(tz)),
                    datetime.fromisoformat(
                        arrival_scheduled).astimezone(pytz.timezone(tz))
                )
            
        elif arrival_estimated is not None:
            arr_hour = datetime.fromisoformat(arrival_estimated).astimezone(
                pytz.timezone(tz)).strftime("%H")
            if datetime.fromisoformat(arrival_estimated).astimezone(pytz.timezone(tz)) <= current_time:
                flight_status = 'landed'
                arrival_delay = mins_between(
                    datetime.fromisoformat(
                        arrival_estimated).astimezone(pytz.timezone(tz)),
                    datetime.fromisoformat(
                        arrival_scheduled).astimezone(pytz.timezone(tz))
                )
            
        elif arrival_scheduled is not None:
            if datetime.fromisoformat(arrival_scheduled).astimezone(pytz.timezone(tz)) <= current_time:
                flight_status = 'landed'

        ##################################################
        # correction of departure delay
        ##################################################
        if departure_actual is not None:
            dep_hour = datetime.fromisoformat(departure_actual).astimezone(
                    pytz.timezone(tz)).strftime("%H")
            if datetime.fromisoformat(departure_actual).astimezone(pytz.timezone(tz)) > datetime.fromisoformat(departure_scheduled).astimezone(pytz.timezone(tz)):
                departure_delay = mins_between(
                    datetime.fromisoformat(
                        departure_actual).astimezone(pytz.timezone(tz)),
                    datetime.fromisoformat(
                        departure_scheduled).astimezone(pytz.timezone(tz))
                )
                
        elif departure_estimated is not None:
            dep_hour = datetime.fromisoformat(departure_estimated).astimezone(
                    pytz.timezone(tz)).strftime("%H")
            if datetime.fromisoformat(departure_estimated).astimezone(pytz.timezone(tz)) > datetime.fromisoformat(departure_scheduled).astimezone(pytz.timezone(tz)):
                departure_delay = mins_between(
                    datetime.fromisoformat(
                        departure_estimated).astimezone(pytz.timezone(tz)),
                    datetime.fromisoformat(
                        departure_scheduled).astimezone(pytz.timezone(tz))
                )
                
        ##################################################
        # Data to be injected in the SQL
        # The Flight_number _ FULL DATE will be my unique key
        # Replacing NONE by null text string
        ##################################################
        flight_key = flight_number + '_' + datetime.fromisoformat(
            departure_scheduled).astimezone(pytz.timezone(tz)).strftime("%d_%m_%Y_%H_%M")
        dep_hour = dep_hour+'h'
        arr_hour = arr_hour+'h'
        flight_extracted = (
            flight_key,
            departure_date,
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
            '' if departure_estimated is None else departure_estimated,
            '' if arrival_estimated is None else arrival_estimated,
            '' if departure_actual is None else departure_actual,
            '' if arrival_actual is None else arrival_actual,
            '' if departure_delay is None else departure_delay,
            '' if arrival_delay is None else arrival_delay
        )

        ##################################################
        # Updating the SQL TABLE
        # If the unique key exist => It will be updated
        # Else it will be created
        ##################################################
        update_table(flight_key, flight_extracted)
