import datetime as dt
from dataclasses import dataclass, field

from folio.models import (
    Book,
    Work,
    TextFormat,
    AudioFormat,
    FormatType,
)


@dataclass(frozen=True)
class Defaults:
    """Immutable default test data for all models."""

    WORK: dict = field(
        default_factory=lambda: {
            "title": "Abril Jacarandil",
            "author": "Josu Roldan",
            "year": 2024,
            "genre": "Poetry",
            "is_read": False,
        }
    )

    TEXT_FORMAT: dict = field(
        default_factory=lambda: {
            "pages": 127,
            "format_type": FormatType.PRINT,
        }
    )

    AUDIO_FORMAT: dict = field(
        default_factory=lambda: {
            "duration": dt.timedelta(hours=8, minutes=45),
            "narrator": "Jane Doe",
        }
    )

    BOOK: dict = field(
        default_factory=lambda: {
            "isbn": "9786079818180",
        }
    )

    TRAVEL: dict = field(
        default_factory=lambda: {
            "origin": "NYC",
            "destination": "LON",
            "date": dt.date(2020, 1, 1),
            "notes": "Vacation",
        }
    )

    ADDRESS: dict = field(
        default_factory=lambda: {
            "start": dt.date(2020, 1, 1),
            "end": None,
            "street_address": "123 Main",
            "province": "ON",
            "country": "Canada",
            "postal_code": "A1B2C3",
        }
    )

    EMPLOYMENT: dict = field(
        default_factory=lambda: {
            "start": dt.date(2020, 1, 1),
            "end": None,
            "company": "Acme",
            "supervisor": "Wild E. Coyote",
            "address": "123 Some St",
            "phone": "555-1234",
        }
    )


DEFAULTS = Defaults()

# Parametrized test data for each model
WORKS = [
    DEFAULTS.WORK,
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
    {
        "work": Work(**DEFAULTS.WORK),
        "format_data": TextFormat(**DEFAULTS.TEXT_FORMAT),
        "isbn": DEFAULTS.BOOK["isbn"],
    },
    {
        "work": Work(**WORKS[1]),  # Hyperion
        "format_data": AudioFormat(
            duration=dt.timedelta(hours=20, minutes=15),
            narrator="Marc Thompson",
        ),
        "isbn": "9780553283686",
    },
    {
        "work": Work(**WORKS[2]),  # The Histories
        "format_data": TextFormat(
            pages=747,
            format_type=FormatType.EBOOK,
        ),
        "isbn": "9780698151369",
    },
]

TRAVELS = [
    DEFAULTS.TRAVEL,
    {
        "origin": "PAR",
        "destination": "ROM",
        "date": dt.date(2021, 5, 15),
        "notes": "Business trip",
    },
    {
        "origin": "TOK",
        "destination": "SYD",
        "date": dt.date(2019, 9, 23),
        "notes": "Conference",
    },
]

ADDRESSES = [
    DEFAULTS.ADDRESS,
    {
        "start": dt.date(2018, 6, 1),
        "end": dt.date(2020, 5, 31),
        "street_address": "456 Elm St",
        "province": "BC",
        "country": "Canada",
        "postal_code": "X9Y8Z7",
    },
    {
        "start": dt.date(2021, 1, 1),
        "end": None,
        "street_address": "789 Oak Ave",
        "province": "CA",
        "country": "USA",
        "postal_code": "90210",
    },
]

EMPLOYMENTS = [
    DEFAULTS.EMPLOYMENT,
    {
        "start": dt.date(2015, 4, 1),
        "end": dt.date(2019, 10, 31),
        "company": "Globex",
        "supervisor": "Hank Scorpio",
        "address": "100 Corporate Plaza",
        "phone": "555-5678",
    },
    {
        "start": dt.date(2020, 6, 15),
        "end": None,
        "company": "Soylent Corp",
        "supervisor": "Linda Lovelace",
        "address": "42 Industrial Blvd",
        "phone": "555-2468",
    },
]
