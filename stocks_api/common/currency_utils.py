import re
from decimal import Decimal


def convert_currency_string(currency_str: str) -> dict:
    pattern = r"([^\d]*)([\d.]+)([TMBK]?)"
    match = re.match(pattern, currency_str.strip())

    if not match:
        raise ValueError("Invalid currency format")

    currency_symbol, value_str, suffix = match.groups()

    multipliers = {
        "T": 1_000_000_000_000,  # Trillion
        "B": 1_000_000_000,  # Billion
        "M": 1_000_000,  # Million
        "K": 1_000,  # Thousand
        "": 1,  # No suffix
    }

    multiplier = multipliers.get(suffix.upper(), 1)
    value = Decimal(value_str) * Decimal(multiplier)
    return {"currency": currency_symbol, "value": float(value)}
