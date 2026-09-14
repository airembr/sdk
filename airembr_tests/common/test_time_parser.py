from datetime import datetime

from airembr.core.time.parser import parse_date_string, parse_date_delta

def test_parse_date():
    dt = parse_date_string("2023-01-01 12:00:00")
    assert isinstance(dt, datetime)
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 1
    
    assert parse_date_string("not a date") is None
    
    # Fuzzy parsing
    dt_fuzzy = parse_date_string("Today is 2023-01-01", fuzzy=True)
    assert isinstance(dt_fuzzy, datetime)
    assert dt_fuzzy.year == 2023

def test_parse_date_delta():
    # parse_date_delta returns seconds as int (from pytimeparse)
    assert parse_date_delta("1m") == 60
    assert parse_date_delta("1h") == 3600
    assert parse_date_delta("1d") == 86400
    assert parse_date_delta("2 mins") == 120
    assert parse_date_delta("not a delta") is None
