import math
import pytest
from exforparser.submodules.utilities.util import (
    is_valid_number,
    safe_float,
    get_number_from_string,
    get_str_from_string,
    split_by_number,
    correct_pub_year,
    cos_to_angle_degrees,
)


def test_is_valid_number_with_int():
    assert is_valid_number(0) is True      # zero must not be treated as None

def test_is_valid_number_with_float():
    assert is_valid_number(3.14) is True

def test_is_valid_number_with_string_number():
    assert is_valid_number("1.5") is True

def test_is_valid_number_with_none():
    assert is_valid_number(None) is False

def test_is_valid_number_with_blank():
    assert is_valid_number("  ") is False


def test_safe_float_valid():
    assert safe_float("2.5", default=0.0) == 2.5

def test_safe_float_invalid_returns_default():
    assert safe_float("abc", default=-1.0) == -1.0


def test_get_number_from_string():
    assert get_number_from_string("Br077") == "077"
    assert get_number_from_string("U-238") == "238"

def test_get_str_from_string():
    assert get_str_from_string("Br077") == "Br"
    assert get_str_from_string("077m") == "m"

def test_split_by_number():
    assert split_by_number("Br077") == ["Br", "077", ""]
    assert split_by_number("Br077m") == ["Br", "077", "m"]


@pytest.mark.parametrize("year_in, expected", [
    ("68",     "1968"),
    ("1968",   "1968"),
    ("196809", "1968"),
    ("200109", "2001"),
    ("20001120", "2000"),
])
def test_correct_pub_year(year_in, expected):
    assert correct_pub_year(year_in) == expected


def test_cos_to_angle_degrees_zero():
    assert cos_to_angle_degrees(1.0) == pytest.approx(0.0)

def test_cos_to_angle_degrees_90():
    assert cos_to_angle_degrees(0.0) == pytest.approx(90.0)

def test_cos_to_angle_degrees_out_of_range():
    with pytest.raises(ValueError):
        cos_to_angle_degrees(1.5)
