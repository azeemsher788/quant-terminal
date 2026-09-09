from typing import List
from werkzeug.exceptions import BadRequest


def parse_ticker_list(param_value: str, default: str = "") -> List[str]:
    """
    Parses a comma-separated string of tickers into a clean, uppercase list.
    Raises BadRequest if the resulting list is empty and no valid default can be formed.
    """
    if not param_value:
        param_value = default

    tickers = [t.strip().upper() for t in param_value.split(",") if t.strip()]
    if not tickers:
        raise BadRequest("Invalid tickers format. Must provide at least one ticker.")
    return tickers


def parse_int_param(param_value: str, default: int, min_val: int, max_val: int) -> int:
    """
    Parses an integer from a string parameter, ensuring it falls within [min_val, max_val].
    Raises BadRequest if it's not a valid integer.
    """
    if not param_value:
        return default

    try:
        val = int(param_value)
        return min(max(min_val, val), max_val)
    except ValueError:
        raise BadRequest("Invalid parameter format. Must be an integer.")
