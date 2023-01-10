"""
Module to generate and handle the Airports Metadata
"""
#!/usr/bin/python3
import json
import os
from argparse import ArgumentParser
from collections import namedtuple
from string import ascii_uppercase

ASCII_UPPERCASE = set(ascii_uppercase)
Airport = namedtuple(
    "Airport",
    [
        "name",
        "city",
        "country",
        "iata",
        "icao",
        "lat",
        "lon",
        "alt",
        "tz",
        "dst",
        "tzdb",
    ],
)
Other = namedtuple(
    "Other", ["iata", "name", "country", "subdiv", "type", "lat", "lon"]
)

# Name       Name of airport. May or may not contain the City name.
# City       Main city served by airport. May be spelled differently from Name.
# Country    Country or territory where airport is located.
# IATA       3-letter FAA code, for airports located in Country "United States of America" and 3-letter IATA code,
#            for all other airports. Blank if not assigned.
# ICAO       4-letter ICAO code and Blank if not assigned.
# Latitude   Decimal degrees, usually to six significant digits. Negative is South, positive is North.
# Longitude  Decimal degrees, usually to six significant digits. Negative is West, positive is East.
# Altitude   In feet!
# Timezone   Hours offset from UTC. Fractional hours are expressed as decimals, eg. India is 5.5.
# DST        Daylight savings time. One of E (Europe), A (US/Canada), S (South America), O (Australia),
#            Z (New Zealand), N (None) or U (Unknown). See also: Help: Time
# Tz database time zone   Timezone in "tz" (Olson) format, eg. "America/Los_Angeles".

# Note: Rules for daylight savings time change from year to year and from country to country. The current data is an
# approximation for 2009, built on a country level. Most airports in DST-less regions in countries that generally
# observe DST (eg. AL, HI in the USA, NT, QL in Australia, parts of Canada) are marked incorrectly.
airport_list = os.path.join(
    os.path.abspath(os.curdir), "data_pipeline/json_data/airport_list.json"
)
other_list = os.path.join(
    os.path.abspath(os.curdir), "data_pipeline/json_data/other_list.json"
)
with open(airport_list, "r", encoding="UTF-8") as f:
    AIRPORT_LIST = json.load(f)
with open(other_list, "r", encoding="UTF-8") as f:
    OTHER_LIST = json.load(f)


class AirportNotFoundException(Exception):
    """
    Class not found exception
    """


class Airports(object):
    """
    Main Airport class
    """

    def __init__(self):

        self.airports = {_[3].upper(): Airport(*_) for _ in AIRPORT_LIST}

        self.other = {_[0].upper(): Other(*_) for _ in OTHER_LIST}

    @staticmethod
    def _validate(iata):
        if not isinstance(iata, str):
            raise ValueError(f"iata must be a string, it is a {type(iata)}")
        iata = iata.strip().upper()
        if len(iata) != 3:
            raise ValueError("iata must be three characters")
        return iata

    def airport_iata(self, iata):
        """
        return airport iata

        :param iata: (str)
        :return: (airport)
        """
        return self.lookup(iata, self.airports)

    def other_iata(self, iata):
        """
        return metadata

        :param iata: (str)
        :return: (airpot)
        """
        return self.lookup(iata, self.other)

    def is_valid(self, iata):
        """
        return metadata

        :param iata: (str)
        :return: (airpot)
        """
        iata = self._validate(iata)
        return iata in self.airports or iata in self.other

    def lookup(self, iata, table=None):
        """
        lookup function

        :param iata: (str)
        :param table: (str), defaults to None
        :raises AirportNotFoundException: _description_
        :raises AirportNotFoundException: _description_
        :return: _description_
        """
        iata = self._validate(iata)

        if not self.is_valid(iata):
            raise AirportNotFoundException(
                f"iata not found in either airport list: {iata}"
            )

        if table is None:
            # Prefer self.airports over self.other
            return self.airports.get(iata) or self.other.get(iata)
        elif iata not in table:
            raise AirportNotFoundException(f"iata not found: {iata}")

        return table.get(iata)


def main():  # pragma: no cover
    """
    Main function
    """

    parser = ArgumentParser("Airport lookup by IATA code")
    parser.add_argument("iata", action="store")
    args = parser.parse_args()
    airports = Airports()
    try:
        print(airports.lookup(args.iata))
    except AirportNotFoundException:
        print("Not in core airport list")


if __name__ == "__main__":  # pragma: no cover
    main()
