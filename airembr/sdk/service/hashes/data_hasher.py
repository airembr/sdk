from hashlib import sha1, md5
import json

def hash_dict_64(obj, dump_schema=True):
    if dump_schema:
        obj_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
    else:
        obj_bytes = str(obj).encode('utf-8')

    return md5(obj_bytes).hexdigest()



def merge_value_as_hash_id(field_value: str) -> str:
    return sha1(str(field_value).encode()).hexdigest()
