import re


class ValidationError(Exception):
    pass


def normalize_phone(raw):
    """Accepts 07XXXXXXXX, 01XXXXXXXX, 2547XXXXXXXX, 2541XXXXXXXX, +254...
    Returns 254XXXXXXXXX — the format Daraja's STK push endpoint requires."""
    if not raw:
        raise ValidationError("Phone number is required")

    digits = re.sub(r"\D", "", str(raw))

    if digits.startswith("254") and len(digits) == 12:
        normalized = digits
    elif digits.startswith("0") and len(digits) == 10:
        normalized = "254" + digits[1:]
    elif (digits.startswith("7") or digits.startswith("1")) and len(digits) == 9:
        normalized = "254" + digits
    else:
        raise ValidationError("Invalid phone number format")

    if not re.match(r"^254(7|1)\d{8}$", normalized):
        raise ValidationError("Invalid Safaricom phone number")

    return normalized
