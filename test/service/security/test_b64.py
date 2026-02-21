from pydantic import BaseModel
from airembr.sdk.service.security.b64 import b64_encoder, b64_decoder, encrypt, decrypt

class MockModel(BaseModel):
    name: str
    value: int

def test_b64_encode_decode_dict():
    data = {"hello": "world", "nested": {"a": 1}}
    encoded = b64_encoder(data)
    assert isinstance(encoded, str)
    
    decoded = b64_decoder(encoded)
    assert decoded == data

def test_b64_encode_decode_model():
    data = MockModel(name="test", value=123)
    encoded = b64_encoder(data)
    
    decoded = b64_decoder(encoded)
    # b64_decoder returns a dict
    assert decoded == {"name": "test", "value": 123}

def test_encrypt_decrypt():
    data = {"secret": "message"}
    encrypted = encrypt(data)
    decrypted = decrypt(encrypted)
    assert decrypted == data

def test_b64_decoder_none():
    assert b64_decoder(None) is None

def test_b64_decoder_invalid_gzip():
    import base64
    import json
    # Just base64 encoded JSON without gzip
    data = {"a": 1}
    encoded = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
    
    # b64_decoder handles OSError from gzip.decompress and returns json.loads(decoded)
    # Wait, if gzip.decompress fails, it catches OSError.
    # But decoded is still the result of base64.b64decode.
    decoded = b64_decoder(encoded)
    assert decoded == data
