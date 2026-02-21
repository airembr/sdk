from datetime import datetime
from zoneinfo import ZoneInfo
from airembr.sdk.common.date import now_in_utc, is_timezone_aware, add_utc_time_zone_if_none, seconds_to_minutes_seconds
import pytest

def test_now_in_utc():
    now = now_in_utc()
    assert is_timezone_aware(now)
    assert now.tzinfo == ZoneInfo('UTC')
    
    # Test with delay
    future = now_in_utc(delay=60)
    assert (future - now).total_seconds() == pytest.approx(60, abs=1)
    
    past = now_in_utc(delay=-60)
    assert (now - past).total_seconds() == pytest.approx(60, abs=1)

def test_is_timezone_aware():
    aware_dt = datetime.now(ZoneInfo('UTC'))
    naive_dt = datetime.now()
    assert is_timezone_aware(aware_dt)
    assert not is_timezone_aware(naive_dt)

def test_add_utc_time_zone_if_none():
    assert add_utc_time_zone_if_none(None) is None
    
    naive_dt = datetime(2023, 1, 1, 12, 0, 0)
    aware_dt = add_utc_time_zone_if_none(naive_dt)
    assert is_timezone_aware(aware_dt)
    assert aware_dt.tzinfo == ZoneInfo('UTC')
    
    already_aware = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Europe/Berlin'))
    result_dt = add_utc_time_zone_if_none(already_aware)
    assert result_dt.tzinfo == ZoneInfo('Europe/Berlin')

def test_seconds_to_minutes_seconds():
    assert seconds_to_minutes_seconds(0) == "0:00.000"
    assert seconds_to_minutes_seconds(61.5) == "1:01.500"
    assert seconds_to_minutes_seconds(3661) == "61:01.000"
    assert seconds_to_minutes_seconds(-61.5) == "-1:01.500"
