import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import requests

import src.utils as U
from data_pipeline.api_requests import fatal_code


class TestTimeAttribute:
    def test_valid_init(self):
        time_str = "2022-01-01T10:00:00"
        ta = U.TimeAttribute(time_str)
        assert isinstance(ta.datetime, datetime)

    def test_invalid_init(self):
        time_str = "2022-01-01T10:00:00"
        ta = U.TimeAttribute(time_str)
        assert ta.datetime.strftime("%Y-%m-%dT%H:%M:%S%z") != time_str

    def test_get_mins_between(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=30)
        ta = U.TimeAttribute(start_date)
        assert ta.get_mins_between(end_date) == 30

    def test_get_days_between(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=5)
        ta = U.TimeAttribute(start_date)
        assert ta.get_days_between(end_date) == 5


def test_is_blank():
    assert not U.is_blank("5")
    assert U.is_blank("")


def test_remove_non_alphanumeric():
    test_str = "Test 123 !@# string"
    expected_output = "Test 123  string"
    assert U.remove_non_alphanumeric(test_str) == expected_output

    test_str = "!@# Test 123 string"
    expected_output = " Test 123 string"
    assert U.remove_non_alphanumeric(test_str) == expected_output

    test_str = "Test 123 string !@#"
    expected_output = "Test 123 string "
    assert U.remove_non_alphanumeric(test_str) == expected_output

    test_str = "!@# Test 123 string !@#"
    expected_output = " Test 123 string "
    assert U.remove_non_alphanumeric(test_str) == expected_output

    test_str = None
    expected_output = ""
    assert U.remove_non_alphanumeric(test_str) == expected_output


def test_get_airport_country():
    airport_iata = "CDG"
    expected_output = "FRANCE"
    assert U.get_airport_country(airport_iata) == expected_output

    airport_iata = "JFK"
    expected_output = "UNITED STATES"
    assert U.get_airport_country(airport_iata) == expected_output

    airport_iata = "XXX"
    expected_output = "UNKNOWN"
    assert U.get_airport_country(airport_iata) == expected_output

    airport_iata = None
    with pytest.raises(AssertionError) as excinfo:
        U.get_airport_country(airport_iata)
    assert "Wrong Type: airport_iata must be a string" in str(excinfo.value)


def test_get_airport_name():
    # Test valid airport IATA code
    airport_iata = "CDG"
    expected_name = "CHARLES DE GAULLE"
    assert U.get_airport_name(airport_iata) == expected_name

    # Test invalid airport IATA code
    airport_iata = "XXX"
    assert U.get_airport_name(airport_iata) == "UNKNOWN"


def test_convert_hex_to_rgb():
    value = "#ff0000"
    expected_output = (255, 0, 0)
    assert U.convert_hex_to_rgb(value) == expected_output

    value = "#00ff00"
    expected_output = (0, 255, 0)
    assert U.convert_hex_to_rgb(value) == expected_output

    value = "#0000ff"
    expected_output = (0, 0, 255)
    assert U.convert_hex_to_rgb(value) == expected_output

    value = "#f0f0f0"
    expected_output = (240, 240, 240)
    assert U.convert_hex_to_rgb(value) == expected_output

    value = "f0f0f0"
    expected_output = (240, 240, 240)
    assert U.convert_hex_to_rgb(value) == expected_output

    with pytest.raises(AssertionError):
        U.convert_hex_to_rgb(123)
        U.convert_hex_to_rgb("invalid_hex_code")


class TestFileFolderManager:
    def test_valid_init(self):
        directory = "test_directory"
        name_file = "test_file.json"
        ffm = U.FileFolderManager(directory, name_file)
        assert isinstance(ffm, U.FileFolderManager)
        assert ffm.name_file == name_file
        assert ffm.dir == directory
        assert Path(ffm.local_dir).is_dir()
        assert ffm.file_exist is False

    def test_invalid_init(self):
        directory = None
        name_file = ""
        with pytest.raises(AssertionError) as excinfo:
            ffm = U.FileFolderManager(directory, name_file)
        assert "name_file must not be an empty string" in str(excinfo.value)

    def test_read_json(self):
        with TemporaryDirectory() as temp_dir:
            ffm = U.FileFolderManager(temp_dir, "test_file.json")
            default_dict = {"test_key": "test_value"}
            ffm.save_json(default_dict)
            assert ffm.read_json() == default_dict

    def test_save_json(self):
        with TemporaryDirectory() as temp_dir:
            ffm = U.FileFolderManager(temp_dir, "test_file.json")
            test_dict = {"test_key": "test_value"}
            ffm.save_json(test_dict)
            assert json.load(open(ffm.file_dir)) == test_dict


def test_fatal_code():
    response = requests.Response()
    response.status_code = 400
    assert fatal_code(response) == True
