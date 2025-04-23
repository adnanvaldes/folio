from utils import is_valid_isbn_10, is_valid_isbn_13


def test_isbn_10():
    # Valid ISBN-10s
    assert is_valid_isbn_10("048665088X") == True
    assert is_valid_isbn_10("123456789x") == True
    assert is_valid_isbn_10("0306406152") == True
    assert is_valid_isbn_10("0198526636") == True
    assert is_valid_isbn_10("0-306-40615-2") == True  # With hyphens
    assert is_valid_isbn_10("0 306 40615 2") == True  # With spaces
    assert is_valid_isbn_10(1933988673) == True  # Not a string

    # Invalid ISBN-10s
    assert is_valid_isbn_10("abcdefghij") == False  # Non-digits
    assert is_valid_isbn_10("04866X5088") == False  # X not in last position
    assert is_valid_isbn_10("04866588X") == False  # Incorrect checksum
    assert is_valid_isbn_10("048665088") == False  # Too short
    assert is_valid_isbn_10("04866508811") == False  # Too long
    assert is_valid_isbn_10("0486650880") == False  # Invalid checksum
    assert is_valid_isbn_10("") == False  # Empty string
    assert is_valid_isbn_10("048665088Y") == False  # Invalid character


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


def test_isbn_10_to_13():
    # TODO: Implement conversion tests once function is created
    pass
