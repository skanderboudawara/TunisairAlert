import requests  # APIs
import os  # Create and organize folders
import json  # Json manipulations
from datetime import datetime, timedelta  # datetime
import pytz  # timezone
from utils.utility import mins_between, days_between
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
    if not(os.path.exists(os.path.join(os.path.abspath(os.curdir), 'token.txt'))):
        with open(os.path.join(os.path.abspath(os.curdir), 'token.txt'), 'w') as f:
            pass

    with open(os.path.join(os.path.abspath(os.curdir), 'token.txt')) as f:
        lines = f.readlines()
        if (len(lines) <= 0):
            print('You need to register to airlabs.co and put the token in the token.txt file')
            return
        _token = lines[0]
    if (_token == '') | (_token is None):
        print('You need to register to airlabs.co and put the token in the token.txt file')
        return
    # File and dir checking
    # current_time = (datetime.now()- timedelta(days=1)).astimezone(pytz.timezone(tz)) # To be used for yesterday
    current_time = datetime.now().astimezone(pytz.timezone(tz))
    print(current_time)
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
        print(f'https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata=TUN&airline_iata=TU&api_key={_token}')
        response = requests.get(
            f'https://airlabs.co/api/v9/schedules?{type_flight[:3]}_iata=TUN&airline_iata=TU&api_key={_token}')
        if response.json():
            with open(f'{path_flight_type}/{file_flight_type}', 'w') as f:
                json.dump(response.json(), f)
            json_flight = response.json()

    if (json_flight == {}) | (not('response' in json_flight)) | (json_flight is None):
        print('You need to register to airlabs.co and put the token in the token.txt file')
        print('be careful you may have reached your limit free plan Airlabs API requests')
        return

    # Get the response data
    real_time_flights = json_flight['response']

    # Loop through each flight and  prepare the data
    for flight in real_time_flights:
        flight_number = flight['flight_iata']
        flight_status = flight['status']
        departure_IATA = flight['dep_iata']
        arrival_IATA = flight['arr_iata']

        # I will handle erros if TUNISAIR made some unknown connections
        try:
            departure_airport = Airports().lookup(departure_IATA).city + ' ' + Airports().lookup(departure_IATA).name
        except:
            departure_airport = 'UNKNOWN'
        try:
            arrival_airport = Airports().lookup(arrival_IATA).city + ' ' + Airports().lookup(arrival_IATA).name
        except:
            arrival_airport = 'UNKNOWN'

        departure_scheduled = flight['dep_time']
        arrival_scheduled = flight['arr_time']
        
        # Handling if exist
        departure_estimated = flight['dep_estimated'] if 'dep_estimated' in flight else None
        arrival_estimated = flight['arr_estimated'] if 'arr_estimated' in flight else None
        departure_actual = flight['dep_actual'] if 'dep_actual' in flight else None
        arrival_actual = flight['arr_actual'] if 'arr_actual' in flight else None
        departure_delay = flight['delayed'] if 'delayed' in flight else 0
        arrival_delay = flight['delayed'] if 'delayed' in flight else 0

        # Conversion to datetime
        datetime_arrival_scheduled = datetime.fromisoformat(arrival_scheduled).astimezone(pytz.timezone(tz))
        datetime_departure_scheduled = datetime.fromisoformat(departure_scheduled).astimezone(pytz.timezone(tz))
        dep_hour = datetime_departure_scheduled.strftime("%H")
        arr_hour = datetime_arrival_scheduled.strftime("%H")
        departure_date = datetime_departure_scheduled.strftime("%d/%m/%Y")
        arrival_date = datetime_departure_scheduled.strftime("%d/%m/%Y")
        ##################################################
        # I have seen that the  flight status and delays are sometimes wrong and needs to be corrected
        # Correction of landing
        # Correction of arrival delay
        ##################################################
        
        if arrival_actual is not None:
            datime_arrival_actual = datetime.fromisoformat(arrival_actual).astimezone(pytz.timezone(tz))
            arr_hour = datime_arrival_actual.strftime("%H")
            arrival_date = datime_arrival_actual.strftime("%d/%m/%Y")
            if datime_arrival_actual <= current_time:
                flight_status = 'landed'
                arrival_delay = mins_between(datime_arrival_actual,datetime_arrival_scheduled)
            if days_between(datime_arrival_actual,datetime_arrival_scheduled) != 0:
                flight_status = 'cancelled'
        elif arrival_estimated is not None:
            datetime_arrival_estimated = datetime.fromisoformat(arrival_estimated).astimezone(pytz.timezone(tz))
            arr_hour = datetime_arrival_estimated.strftime("%H")
            arrival_date = datetime_arrival_estimated.strftime("%d/%m/%Y")
            if datetime_arrival_estimated <= current_time:
                flight_status = 'landed'
                arrival_delay = mins_between(datetime_arrival_estimated,datetime_arrival_scheduled)
            if days_between(datetime_arrival_estimated,datetime_arrival_scheduled) != 0:
                flight_status = 'cancelled'
        elif arrival_scheduled is not None:
            if datetime_arrival_scheduled <= current_time:
                flight_status = 'landed'

        ##################################################
        # correction of departure delay
        ##################################################
        if departure_actual is not None:
            datetime_departure_actual = datetime.fromisoformat(departure_actual).astimezone(pytz.timezone(tz))
            dep_hour = datetime_departure_actual.strftime("%H")
            departure_date = datetime_departure_actual.strftime("%d/%m/%Y")
            if datetime_departure_actual > datetime_departure_scheduled:
                departure_delay = mins_between(datetime_departure_actual,datetime_departure_scheduled)
            if days_between(datetime_departure_actual,datetime_departure_scheduled) != 0:
                flight_status = 'cancelled'
        elif departure_estimated is not None:
            datetime_departure_estimated = datetime.fromisoformat(departure_estimated).astimezone(pytz.timezone(tz))
            dep_hour = datetime_departure_estimated.strftime("%H")
            departure_date = datetime_departure_estimated.strftime("%d/%m/%Y")
            if datetime_departure_estimated > datetime_departure_scheduled:
                departure_delay = mins_between(datetime_departure_estimated,datetime_departure_scheduled)
            if days_between(datetime_departure_estimated,datetime_departure_scheduled) != 0:
                flight_status = 'cancelled'

        ##################################################
        # Data to be injected in the SQL
        # The Flight_number _ FULL DATE will be my unique key
        # Replacing NONE by null text string
        ##################################################
        flight_key = flight_number + '_' + datetime_departure_scheduled.strftime("%d_%m_%Y_%H_%M")
        dep_hour = dep_hour+'h'
        arr_hour = arr_hour+'h'
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
