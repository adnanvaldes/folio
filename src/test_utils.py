from utils import is_valid_isbn_10, is_valid_isbn_13, convert_isbn_10_to_13

"""
Tests created with the help of Claude 3.7 Sonnet.

Note: some manual intervention was implemented to avoid LLM-hallucinated
tests, in particular with the creation of valid/invalid ISBNs
"""


def test_isbn_10():
    # Valid ISBN-10s
    assert is_valid_isbn_10("048665088X") == True
    assert is_valid_isbn_10("123456789x") == True
    assert is_valid_isbn_10("0306406152") == True
    assert is_valid_isbn_10("0198526636") == True
    assert is_valid_isbn_10("0-306-40615-2") == True  # With hyphens
    assert is_valid_isbn_10("0 306 40615 2") == True  # With spaces
    assert is_valid_isbn_10(1933988673) == True  # Not a string
    assert is_valid_isbn_10("0000000000") == True
    assert is_valid_isbn_10(9999999999) == True

    # Invalid ISBN-10s
    assert is_valid_isbn_10("abcdefghij") == False  # Non-digits
    assert is_valid_isbn_10("04866X5088") == False  # X not in last position
    assert is_valid_isbn_10("04866588X") == False  # Incorrect checksum
    assert is_valid_isbn_10("048665088") == False  # Too short
    assert is_valid_isbn_10("04866508811") == False  # Too long
    assert is_valid_isbn_10("0486650880") == False  # Invalid checksum
    assert is_valid_isbn_10("") == False  # Empty string
    assert is_valid_isbn_10("048665088Y") == False  # Invalid character
    assert is_valid_isbn_10("999999999X") == False


def test_isbn_13():
    # Valid ISBN-13s
    assert is_valid_isbn_13("9781861978769") == True
    assert is_valid_isbn_13("9780306406157") == True  # Converted from valid ISBN-10
    assert is_valid_isbn_13("9780132350884") == True
    assert is_valid_isbn_13("9781449340377") == True
    assert is_valid_isbn_13("978-0-306-40615-7") == True  # With hyphens
    assert is_valid_isbn_13("978 0 306 40615 7") == True  # With spaces
    assert is_valid_isbn_13(9781861978769) == True  # Not a string

    # Invalid ISBN-13s
    assert is_valid_isbn_13("9781861978768") == False  # Invalid checksum
    assert is_valid_isbn_13("978186197876") == False  # Too short
    assert is_valid_isbn_13("97818619787691") == False  # Too long
    assert is_valid_isbn_13("978186197876A") == False  # Invalid character
    assert is_valid_isbn_13("") == False  # Empty string
    assert is_valid_isbn_13("9780132350884A") == False  # Too long with


def test_isbn_10_to_13():
    # Basic tests with both string and integer inputs
    assert convert_isbn_10_to_13("1861972717") == "9781861972712"
    assert convert_isbn_10_to_13(1861972717) == "9781861972712"

    # Test with hyphens and spaces in input
    assert convert_isbn_10_to_13("1-86197-271-7") == "9781861972712"
    assert convert_isbn_10_to_13("1 86197 271 7") == "9781861972712"

    # Test with 'X' as check digit (represents 10)
    assert convert_isbn_10_to_13("080442957X") == "9780804429573"
    assert convert_isbn_10_to_13("0-8044-2957-X") == "9780804429573"
    assert convert_isbn_10_to_13("0-8044-2957-x") == "9780804429573"  # lowercase x

    # Test with zero check digit
    assert convert_isbn_10_to_13("0306406152") == "9780306406157"

    # Test boundary conditions
    assert convert_isbn_10_to_13("0000000000") == "9780000000002"  # All zeros
    assert convert_isbn_10_to_13("9999999999") == "9789999999991"  # Highest possible

    # Test invalid inputs - should return None
    assert convert_isbn_10_to_13("123456789") is None  # Too short
    assert convert_isbn_10_to_13("12345678901") is None  # Too long
    assert convert_isbn_10_to_13("ABCDEFGHIJ") is None  # Non-numeric
    assert convert_isbn_10_to_13("") is None  # Empty string
    assert convert_isbn_10_to_13(None) is None  # None input
    assert (
        convert_isbn_10_to_13("1-23-45678-9") is None
    )  # Invalid checksum despite format
