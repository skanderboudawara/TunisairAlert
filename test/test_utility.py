import src.utils as U
import pytest
from datetime import datetime
from pathlib import Path
import os


def test_is_blank():
    assert not U.is_blank("5")
    assert U.is_blank('')


def test_remove_non_alphanumeric():
    assert "5" == U.remove_non_alphanumeric("5")
    assert "AB" == U.remove_non_alphanumeric('A-B')
    assert "" == U.remove_non_alphanumeric(None)
    assert "" == U.remove_non_alphanumeric("")
    with pytest.raises(AssertionError, match="^Wrong Type"):
        U.remove_non_alphanumeric(5)


def test_TimeAttribute():

    date1 = "2019-09-26T07:58:30.996+0200"
    D = U.TimeAttribute(date1)

    assert D.dateformat == "26/09/2019"
    assert D.full_hour == "06:58"
    assert D.full_day == "Thu 26 Sep 2019"
    assert D.hour == "06"
    assert D.month == "09"
    assert D.full_under_score == "26_09_2019_06_58"
    assert D.short_under_score == "26_09_2019"

    with pytest.raises(AssertionError, match="^Wrong Type"):
        U.TimeAttribute(5)


def test_get_mins_between():
    D = U.TimeAttribute("2022-12-29 23:57:59.342380")
    time2 = datetime(2022, 12, 29, 23, 58, 59, 342380)
    time1 = datetime(2022, 12, 29, 23, 56, 59, 342380)
    assert 1 == D.get_mins_between(time2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        D.get_mins_between("2022/12/28 23:55:59")
    with pytest.raises(AssertionError, match="^Wrong Value"):
        D.get_mins_between(time1)


def test_get_days_between():
    D = U.TimeAttribute("2022-12-29 23:57:59.342380")
    date2 = datetime(2022, 12, 30, 23, 55, 59, 342380)
    date1 = datetime(2022, 12, 26, 23, 55, 59, 342380)
    assert 1 == D.get_days_between(date2)
    with pytest.raises(AssertionError, match="^Wrong Type"):
        D.get_mins_between("2022-12-29 23:57:59.342380")
    with pytest.raises(AssertionError, match="^Wrong Value"):
        D.get_mins_between(date1)


def test_get_airport_country():
    assert "UNKNOWN" == U.get_airport_country("AAAA")
    assert "TUNISIA" == U.get_airport_country("TUN")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        U.get_airport_country(5)


def test_get_airport_name():
    assert "UNKNOWN" == U.get_airport_name("AAAA")
    assert "CARTHAGE" == U.get_airport_name("TUN")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        U.get_airport_name(5)


def test_convert_hex_to_rgb():
    assert (255, 255, 255) == U.convert_hex_to_rgb("#FFFFFF")

    with pytest.raises(AssertionError, match="^Wrong Type"):
        U.convert_hex_to_rgb(5)


def test_FileToFolderManager():
    test_folder = U.FileFolderManager(directory="test", name_file="test.json")
    assert test_folder.name_file == "test.json"
    assert test_folder.dir == "test"
    assert test_folder.file_exist == False

    assert {'a': 2} == test_folder.read_json({'a': 2})

    os.remove(test_folder.file_dir)

    test_folder2 = U.FileFolderManager(directory="test", name_file="test2.json")
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


def test_Fonts():
    assert Path(U.SKYFONT).exists()
    assert Path(U.SKYFONT_INVERTED).exists()
    assert Path(U.GLYPH_AIRPORT).exists()
