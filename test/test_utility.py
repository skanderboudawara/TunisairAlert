import utils.utility as Utils
import pytest
from datetime import datetime
from pathlib import Path
import os


def test_is_blank():
    assert False == Utils.is_blank("5")
    assert True == Utils.is_blank('')
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.is_blank(5)


def test_is_not_blank():
    assert True == Utils.is_not_blank("5")
    assert False == Utils.is_not_blank('')
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.is_not_blank(5)


def test_remove_non_alphanumeric():
    assert "5" == Utils.remove_non_alphanumeric("5")
    assert "AB" == Utils.remove_non_alphanumeric('A-B')
    assert "" == Utils.remove_non_alphanumeric(None)
    assert "" == Utils.remove_non_alphanumeric("")
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.remove_non_alphanumeric(5)


def test_get_mins_between():
    time1 = datetime(2022, 12, 28, 23, 55, 59, 342380)
    time2 = datetime(2022, 12, 28, 23, 57, 59, 342380)
    assert 2 == Utils.get_mins_between(time1, time2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_mins_between("2022/12/28 23:55:59", time2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_mins_between(time1, "2022/12/28 23:55:59")
    with pytest.raises(AssertionError, match="^Wrong Value"):
        Utils.get_mins_between(time2, time1)


def test_get_days_between():
    date1 = datetime(2022, 12, 28, 23, 55, 59, 342380)
    date2 = datetime(2022, 12, 29, 23, 55, 59, 342380)
    assert 1 == Utils.get_days_between(date1, date2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_mins_between("2022/12/28 23:55:59", date2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_mins_between(date1, "2022/12/28 23:55:59")
    with pytest.raises(AssertionError, match="^Wrong Value"):
        Utils.get_mins_between(date2, date1)


def test_get_airport_country():
    assert "UNKNOWN" == Utils.get_airport_country("AAAA")
    assert "TUNISIA" == Utils.get_airport_country("TUN")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_airport_country(5)


def test_get_airport_name():
    assert "UNKNOWN" == Utils.get_airport_name("AAAA")
    assert "CARTHAGE" == Utils.get_airport_name("TUN")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.get_airport_name(5)


def test_convert_hex_to_rgb():
    assert (255, 255, 255) == Utils.convert_hex_to_rgb("#FFFFFF")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.convert_hex_to_rgb(5)


def test_TimeAttribute():

    date1 = "2019-09-26T07:58:30.996+0200"
    D = Utils.TimeAttribute(date1)

    assert D.dateformat == "26/09/2019"
    assert D.full_hour == "06:58"
    assert D.full_day == "Thu 26 Sep 2019"
    assert D.hour == "06"
    assert D.month == "09"
    assert D.full_under_score == "26_09_2019_06_58"
    assert D.short_under_score == "26_09_2019"

    with pytest.raises(AssertionError, match="^Wrong Type"):
        Utils.TimeAttribute(5)


def test_FileToFolderManager():
    test_folder = Utils.FileFolderManager(
        directory="test", name_file="test.json")
    assert test_folder.name_file == "test.json"
    assert test_folder.dir == "test"
    assert test_folder.file_exist == False

    assert {'a': 2} == test_folder.read_json({'a': 2})

    os.remove(test_folder.file_dir)

    test_folder2 = Utils.FileFolderManager(
        directory="test", name_file="test2.json")
    assert test_folder2.name_file == "test2.json"
    assert test_folder2.dir == "test"
    assert test_folder2.file_exist == True

    assert {'test2': 2} == test_folder2.read_json({'a': 2})
    test_folder2.save_json({'b': 2})

    assert {'b': 2} == test_folder2.read_json()

    test_folder2.save_json({'test2': 2})

    with pytest.raises(AssertionError, match="^Wrong Type"):
        test_folder2.save_json(5)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        test_folder2.read_json(5)


def test_FontsTunisAlert():
    c = Utils.FontsTunisAlert()

    assert Path(c.skyfont).exists()
    assert Path(c.skyfontInverted).exists()
    assert Path(c.glyphAirport).exists()
