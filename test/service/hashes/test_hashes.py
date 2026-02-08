import time
from airembr.sdk.service.hashes.hash import dict_hash
from airembr.sdk.service.hashes.sha1_hasher import SHA1Encoder
from airembr.sdk.service.hashes.uuid_generator import get_time_based_uuid

def test_dict_hash():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}
    # Should be deterministic regardless of order
    assert dict_hash(d1) == dict_hash(d2)
    
    d3 = {"a": 1, "b": 3}
    assert dict_hash(d1) != dict_hash(d3)

def test_sha1_encoder():
    data = "test_data"
    # Salted hash: "6qO.IwmWg=#..R7/zICi" + data
    expected_hash = SHA1Encoder.encode(data)
    assert isinstance(expected_hash, str)
    assert len(expected_hash) == 40 # SHA1 length
    
    # Check consistency
    assert SHA1Encoder.encode(data) == expected_hash
    # Check difference
    assert SHA1Encoder.encode("other_data") != expected_hash

def test_get_time_based_uuid():
    uuid1 = get_time_based_uuid(interval_seconds=10)
    assert isinstance(uuid1, str)
    
    # Test determinism within same interval
    # (assuming we don't cross the boundary during the test, 10s should be enough)
    uuid2 = get_time_based_uuid(interval_seconds=10)
    assert uuid1 == uuid2
    
    # Test difference across intervals (mocking time would be better, but let's test logic)
    # We can't easily change time without mocking, but we can test the function with different intervals
    # to see if it produces different results for same time.
    uuid3 = get_time_based_uuid(interval_seconds=1000000)
    # Most likely different due to time_slot calculation
    # assert uuid1 != uuid3 # Not guaranteed but very likely
