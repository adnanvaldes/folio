import re


def is_valid_isbn_10(isbn: str | int) -> bool:
    """
    Checks if a number is a valid ISBN-10.

    Procedure taken from https://isbn-information.com/the-10-digit-isbn.html
    """
    isbn = re.sub(r"[^a-zA-Z0-9]", "", str(isbn))
    isbn_chars = list(str(isbn).lower())

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
    Checks if a number is a valid ISBN-13.

    Procedure taken from https://isbn-information.com/the-13-digit-isbn.html
    """
    isbn = re.sub(r"[^0-9]", "", str(isbn))
    isbn_chars = list(str(isbn))

    # Check that ISBN is exactly 13 digits long and contains only digits
    if len(isbn_chars) != 13 or not all(char.isdigit() for char in isbn_chars):
        return False

    isbn_digits = list(map(int, isbn_chars))

    # Apply ISBN-13 algorithm by alternating multipliers (1,3,1,3,...) to each digit
    products = []
    for i, digit in enumerate(isbn_digits):
        multiplier = 1 if i % 2 == 0 else 3
        products.append(digit * multiplier)

    # ISBN-13 is valid if checksum is divisible by 10
    return sum(products) % 10 == 0


def convert_isbn_10_to_13(isbn10: str) -> str:
    pass
