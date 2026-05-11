def try_number(s):
    """
    Converts a given input into a floating-point number if possible.

    This function attempts to parse the given string or input into a
    floating-point number. If the conversion fails (e.g., due to invalid
    input such as a non-numeric string), the original input is returned
    unchanged.

    :param s: The input value to convert. This can be a string or other
        value to be evaluated.
    :return: The converted floating-point number if the input is a valid
        numeric string. Otherwise, the original input is returned.
    """
    try:
        return float(s)
    except ValueError:
        return s