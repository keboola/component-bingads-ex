def comma_separated_str_to_list(s: str, sep: str = ','):
    return [el.strip() for el in s.split(sep)]
