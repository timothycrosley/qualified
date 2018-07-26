def string_boolean(value):
    """Determines the boolean value for a specified string"""
    if value.lower() in ('false', 'f', '0', ''):
        return False
    else:
        return True
