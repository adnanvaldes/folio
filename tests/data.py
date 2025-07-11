from dataclasses import dataclass
from datetime import date
from folio.models.models import Book, Work


@dataclass(frozen=True)
class Defaults:
    """Immutable default test data for all models."""

    WORK: dict = {
        "title": "Abril Jacarandil",
        "author": "Josu Roldan",
        "year": 2024,
        "genre": "Poetry",
        "is_read": False,
    }

    BOOK: dict = {
        "pages": 127,
        "format": Book.Format.PRINT,
        "isbn": "9786079818180",
    }

    TRAVEL: dict = {
        "origin": "NYC",
        "destination": "LON",
        "date": date(2020, 1, 1),
        "notes": "Vacation",
    }

    ADDRESS: dict = {
        "start": date(2020, 1, 1),
        "end": None,
        "street_address": "123 Main",
        "province": "ON",
        "country": "Canada",
        "postal_code": "A1B2C3",
    }

    EMPLOYMENT: dict = {
        "start": date(2020, 1, 1),
        "end": None,
        "company": "Acme",
        "supervisor": "Wild E. Coyote",
        "address": "123 Some St",
        "phone": "555-1234",
    }


# Parametrized test data for each model
WORKS = [
    Defaults.WORK,
    {
        "title": "Hyperion",
        "author": "Dan Simmons",
        "year": 1989,
        "genre": "Sci-Fi",
        "is_read": True,
    },
    {
        "title": "The Histories",
        "author": "Herodotus",
        "year": -430,
        "genre": "Non-Fiction",
        "is_read": True,
    },
]

BOOKS = [
    Defaults.BOOK,
    {
        "pages": 481,
        "format": Book.Format.AUDIO,
        "isbn": "9780553283686",
    },
    {
        "pages": 747,
        "format": Book.Format.EBOOK,
        "isbn": "9780698151369",
    },
]

TRAVELS = [
    Defaults.TRAVEL,
    {
        "origin": "PAR",
        "destination": "ROM",
        "date": date(2021, 5, 15),
        "notes": "Business trip",
    },
    {
        "origin": "TOK",
        "destination": "SYD",
        "date": date(2019, 9, 23),
        "notes": "Conference",
    },
]

ADDRESSES = [
    Defaults.ADDRESS,
    {
        "start": date(2018, 6, 1),
        "end": date(2020, 5, 31),
        "street_address": "456 Elm St",
        "province": "BC",
        "country": "Canada",
        "postal_code": "X9Y8Z7",
    },
    {
        "start": date(2021, 1, 1),
        "end": None,
        "street_address": "789 Oak Ave",
        "province": "CA",
        "country": "USA",
        "postal_code": "90210",
    },
]

EMPLOYMENTS = [
    Defaults.EMPLOYMENT,
    {
        "start": date(2015, 4, 1),
        "end": date(2019, 10, 31),
        "company": "Globex",
        "supervisor": "Hank Scorpio",
        "address": "100 Corporate Plaza",
        "phone": "555-5678",
    },
    {
        "start": date(2020, 6, 15),
        "end": None,
        "company": "Soylent Corp",
        "supervisor": "Linda Lovelace",
        "address": "42 Industrial Blvd",
        "phone": "555-2468",
    },
]
