def bigint_to_unsigned_hex(value):
    return hex(value & ((1 << 64) - 1))