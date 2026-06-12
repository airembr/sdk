def uuid4_from_md5(hash: str):
    return f"{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:32]}"
