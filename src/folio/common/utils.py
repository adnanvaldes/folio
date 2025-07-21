import re
import inspect
import datetime as dt
from functools import wraps


def normalize_date(date_input):
    if isinstance(date_input, dt.date):
        return date_input.isoformat()

    if isinstance(date_input, str):
        try:
            iso_date = dt.datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_input}")

        return iso_date

    raise TypeError(f"date must be a date or string, {type(date_input)} was passed")


def is_valid_isbn_10(isbn: str | int) -> bool:
    """
    Validates if a number is a valid ISBN-10.

    ISBN-10 validation uses a weighted sum algorithm where each digit
    is multiplied by its position (10 to 1), and the sum must be divisible by 11.

    Args:
        isbn: The ISBN-10 number as string or integer

    Returns:
        bool: True if the ISBN-10 is valid, False otherwise

    Note:
        Hyphens and spaces are removed before validation
        The check digit 'X' represents the value 10
    """
    # Remove any non-alphanumeric characters (spaces, hyphens)
    isbn_cleaned = re.sub(r"[^a-zA-Z0-9]", "", str(isbn))
    isbn_chars = list(isbn_cleaned.lower())

    # ISBN-10 must be exactly 10 characters
    if len(isbn_chars) != 10:
        return False

    # Handle 'x' check digit (represents value 10) in last position
    if isbn_chars[9] == "x":
        isbn_chars[9] = "10"

    # Verify all characters are digits (after 'x' replacement)
    if all(str(char).isdigit() for char in isbn_chars):
        isbn_digits = list(map(int, isbn_chars))

        # Apply ISBN-10 algorithm: sum of (10-position)×digit
        checksum = sum(
            (10 - position) * digit for position, digit in enumerate(isbn_digits)
        )
    else:
        return False

    # ISBN-10 is valid if checksum is divisible by 11
    return checksum % 11 == 0


def is_valid_isbn_13(isbn: str | int) -> bool:
    """
    Validates if a number is a valid ISBN-13.

    ISBN-13 validation uses an alternating weight algorithm where digits are multiplied
    by alternating 1 and 3, and the sum must be divisible by 10.

    Args:
        isbn: The ISBN-13 number as string or integer

    Returns:
        bool: True if the ISBN-13 is valid, False otherwise

    Note:
        Hyphens and spaces are removed before validation
        Only numeric digits are allowed in ISBN-13
    """
    # Remove any non-alphanumeric characters (spaces, hyphens)
    isbn_cleaned = re.sub(r"[^a-zA-Z0-9]", "", str(isbn))
    isbn_chars = list(isbn_cleaned)

    # Check that ISBN is exactly 13 digits long and contains only digits
    if len(isbn_chars) != 13 or not all(char.isdigit() for char in isbn_chars):
        return False

    isbn_digits = list(map(int, isbn_chars))

    # Apply ISBN-13 algorithm by alternating weights (1,3,1,3,...) to each digit
    checksum = 0
    for i, digit in enumerate(isbn_digits):
        weight = 1 if i % 2 == 0 else 3
        checksum += digit * weight

    # ISBN-13 is valid if checksum is divisible by 10
    return checksum % 10 == 0


def convert_isbn_10_to_13(isbn_10: str | int) -> str | None:
    """
    Convert a valid ISBN-10 to ISBN-13 format.

    Args:
        isbn_10: A valid ISBN-10 number as string or integer

    Returns:
        ISBN-13 as string if valid, None otherwise
    """
    if is_valid_isbn_10(isbn_10):
        # Remove any non-alphanumeric characters first
        isbn_10_cleaned = re.sub(r"[^a-zA-Z0-9]", "", str(isbn_10))

        # ISBN-13 starts with "978" prefix + first 9 digits of ISBN-10
        isbn_13_chars = ["9", "7", "8"] + list(isbn_10_cleaned[:-1])
        isbn_13_digits = list(map(int, isbn_13_chars))

        # Calculate ISBN-13 check digit using alternating 1,3 weight pattern
        checksum = 0
        for i, digit in enumerate(isbn_13_digits):
            weight = 1 if i % 2 == 0 else 3
            checksum += digit * weight

        # Check digit is (10 - remainder) unless remainder is 0
        remainder = checksum % 10
        check_digit = 0 if remainder == 0 else 10 - remainder

        # Append check digit and join to form final ISBN-13
        isbn_13_chars.append(str(check_digit))
        return "".join(isbn_13_chars)

    return None


def validate_isbn(isbn) -> str | None:
    if isbn is None:
        return None
    if is_valid_isbn_13(isbn):
        return isbn
    isbn_13 = convert_isbn_10_to_13(isbn)
    if isbn_13 is not None:
        return isbn_13
    raise ValueError(f"Invalid ISBN: {isbn} - must be valid ISBN-10 or ISBN-13")


def lowercase_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            if isinstance(value, str):
                bound.arguments[name] = value.lower()

        return func(*bound.args, **bound.kwargs)

    return wrapper
