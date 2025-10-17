import pytest
import sqlite3
import datetime as dt

from folio.models import Address
from folio.services import AddressService
from folio.uow import AddressSQLiteUoW
from folio.repositories import SQLiteAddressRepository


@pytest.fixture
def address_service(fake_db):
    """Fixture to provide an AddressService instance with a fake database."""
    uow = AddressSQLiteUoW(fake_db)
    return AddressService(uow)


def test_add_and_list_address(address_service, multiple_addresses):
    """Test adding a new address and listing all addresses."""
    data = multiple_addresses
    new_id = address_service.add(
        start=data["start"],
        end=data["end"],
        street=data["street"],
        city=data["city"],
        province=data["province"],
        country=data["country"],
        postal_code=data["postal_code"],
    )
    addresses = address_service.list()

    assert len(addresses) == 1
    addr = addresses[0]
    assert isinstance(addr, Address)
    assert addr.start == data["start"]
    assert addr.end == data["end"]
    assert addr.street == data["street"]
    assert addr.city == data["city"]
    assert addr.province == data["province"]
    assert addr.country == data["country"]
    assert addr.postal_code == data["postal_code"]
    assert new_id == 1


def test_get_address_by_id(address_service):
    """Test retrieving an address by its ID."""
    address_service.add(
        start="2020-01-01",
        street="123 Some Str",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    address_id = 1
    address = address_service.get(address_id)

    assert address is not None
    assert address.start == dt.date(2020, 1, 1)
    assert address.country == "Canada"


def test_prevent_duplicate_address(address_service):
    """Test that duplicate addresses are prevented at the service level."""
    address_service.add(
        start="1900-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )

    with pytest.raises(ValueError) as e:
        address_service.add(
            start="1900-01-01",
            end="1950-01-01",
            street="123 Some Str",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="V6Y 0A0",
        )

    assert "already exists" in str(e.value)


def test_find_address_by_street(address_service):
    """Test finding addresses by street name."""
    address_service.add(
        start="1901-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    address_service.add(
        start="1951-01-01",
        end="2000-01-01",
        street="456 Other Street",
        city="Mexico City",
        country="Mexico",
        postal_code="16040",
    )

    results = address_service.find(street="456 Other Street")
    assert len(results) == 1
    assert results[0].street == "456 Other Street"


def test_delete_by_fields(address_service):
    """Test deleting addresses based on field values."""
    address_service.add(
        start="1901-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    address_service.add(
        start="1951-01-01",
        end="2000-01-01",
        street="456 Other Street",
        city="Mexico City",
        country="Mexico",
        postal_code="16040",
    )

    assert len(address_service.list()) == 2

    service_instance = address_service  # Rename for clarity with fixture

    service_instance.delete(country="Mexico")
    assert len(service_instance.list()) == 1

    service_instance.delete(postal_code="V6Y 0A0")
    assert service_instance.list() == []

    with pytest.raises(ValueError):
        service_instance.delete(city="Vancouver")


# --- Database Constraint Enforcement Tests ---
def test_address_constraints_not_null(fake_db):
    """Test that NOT NULL constraints are enforced directly by the database."""
    # Attempt to insert a record missing required fields (e.g., street)
    with pytest.raises(sqlite3.IntegrityError) as e:
        cursor = fake_db.cursor()
        cursor.execute(
            """
            INSERT INTO addresses (start, city, country, postal_code)
            VALUES (?, ?, ?, ?)
            """,
            ("2023-01-01", "Missingville", "Nowhere", "00000"),
        )
        fake_db.commit()
    assert "NOT NULL constraint failed" in str(e.value)


def test_address_constraints_unique_address(fake_db):
    """Test that UNIQUE constraints are enforced directly by the database
    for the combination of (start, end, street, city, province, country, postal_code)."""
    conn = fake_db
    cursor = conn.cursor()

    # First successful insert
    cursor.execute(
        """
        INSERT INTO addresses (start, end, street, city, province, country, postal_code, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "1900-01-01",
            "1950-01-01",
            "123 Some Str",
            "Vancouver",
            "BC",
            "Canada",
            "V6Y 0A0",
            None,
        ),
    )
    conn.commit()

    # Second insert with identical unique fields should raise an IntegrityError
    with pytest.raises(sqlite3.IntegrityError) as e:
        cursor.execute(
            """
            INSERT INTO addresses (start, end, street, city, province, country, postal_code, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "1900-01-01",
                "1950-01-01",
                "123 Some Str",
                "Vancouver",
                "BC",
                "Canada",
                "V6Y 0A0",
                "Some notes",  # notes field can differ without breaking unique
            ),
        )
        conn.commit()
    assert "UNIQUE constraint failed" in str(e.value)


# --- Data Type Conversion & Serialization Tests ---
def test_date_serialization(address_service):
    """Test date serialization to string and deserialization back to dt.date."""
    start_date = dt.date(2023, 1, 15)
    end_date = dt.date(2023, 12, 31)
    address_service.add(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        street="789 Another Ave",
        city="Toronto",
        country="Canada",
        postal_code="M5H 2N2",
    )
    address = address_service.get(1)
    assert address.start == start_date
    assert address.end == end_date


def test_empty_notes_field(address_service):
    """Test handling of an explicitly empty string for the notes field."""
    address_service.add(
        start="2023-03-01",
        street="101 Main St",
        city="Calgary",
        country="Canada",
        postal_code="T2P 2V7",
        notes="",
    )
    address = address_service.get(1)
    assert address.notes == ""


def test_null_notes_field(address_service):
    """Test handling of None (NULL) for the notes field."""
    address_service.add(
        start="2023-03-01",
        street="101 Main St",
        city="Calgary",
        country="Canada",
        postal_code="T2P 2V7",
        notes=None,
    )
    address = address_service.get(1)
    assert address.notes is None


# --- Transaction Behavior Tests ---
def test_transaction_rollback(fake_db, address_service):
    """Test that a transaction is rolled back on error."""
    initial_count = len(address_service.list())
    try:
        with address_service.uow:  # Using the context manager for transaction
            address_service.add(
                start="2023-04-01",
                street="222 Second St",
                city="Edmonton",
                country="Canada",
                postal_code="T5J 2R3",
            )
            # Force an error by attempting to insert into a non-existent column
            cursor = fake_db.cursor()
            cursor.execute("INSERT INTO addresses (non_existent_column) VALUES ('test')")
            # This commit would normally happen at the end of `with` block,
            # but the error above will trigger an exception and rollback.
    except sqlite3.OperationalError:
        # Expected error from executing bad SQL
        pass
    except Exception as e:
        pytest.fail(f"Unexpected exception during rollback test: {e}")

    # After the `with` block, the transaction should have rolled back.
    # Check that the address was not added
    assert len(address_service.list()) == initial_count


def test_transaction_commit(address_service):
    """Test that a transaction is committed successfully."""
    initial_count = len(address_service.list())
    with address_service.uow:
        address_service.add(
            start="2023-05-01",
            street="333 Third Ave",
            city="Winnipeg",
            country="Canada",
            postal_code="R3B 3N5",
        )
    # After exiting the `with` block, the transaction should be committed.
    assert len(address_service.list()) == initial_count + 1


def test_multiple_operations_in_transaction(address_service):
    """Test that multiple operations within a single transaction are atomic."""
    initial_count = len(address_service.list())
    with address_service.uow:
        address_service.add(
            start="2023-06-01",
            street="444 Fourth Rd",
            city="Halifax",
            country="Canada",
            postal_code="B3H 4R2",
        )
        address_service.add(
            start="2023-07-01",
            street="555 Fifth Blvd",
            city="Montreal",
            country="Canada",
            postal_code="H3A 2T6",
        )
    assert len(address_service.list()) == initial_count + 2


# --- Query Behavior Tests ---
def test_find_case_insensitive(address_service):
    """Test case-insensitive search for string fields like city."""
    address_service.add(
        start="2023-08-01",
        street="666 Sixth Lane",
        city="Quebec City",
        country="Canada",
        postal_code="G1R 2B5",
    )
    # Search with lowercase
    results = address_service.find(city="quebec city")
    assert len(results) == 1
    assert results[0].city == "Quebec City"

    # Search with uppercase
    results = address_service.find(city="QUEBEC CITY")
    assert len(results) == 1
    assert results[0].city == "Quebec City"


def test_find_partial_match(address_service):
    """Test partial match search (e.g., find by partial street name)."""
    address_service.add(
        start="2023-09-01",
        street="777 Seventh Crescent",
        city="Ottawa",
        country="Canada",
        postal_code="K1P 5Z5",
    )
    # Assuming 'find' implements 'LIKE' or similar partial matching
    results = address_service.find(street="Seventh")
    assert len(results) == 1
    assert results[0].street == "777 Seventh Crescent"

    results = address_service.find(street="Crescent")
    assert len(results) == 1
    assert results[0].street == "777 Seventh Crescent"

    results = address_service.find(street="NonExistent")
    assert len(results) == 0


def test_find_with_multiple_criteria(address_service):
    """Test find with multiple filter criteria (AND logic)."""
    address_service.add(
        start="2023-10-01",
        street="888 Eighth Place",
        city="Victoria",
        province="BC",
        country="Canada",
        postal_code="V8W 2Z7",
    )
    address_service.add(
        start="2023-11-01",
        street="999 Ninth Lane",
        city="Victoria",
        province="AUS",
        country="Australia",
        postal_code="3000",
    )

    results = address_service.find(city="Victoria", province="BC")
    assert len(results) == 1
    assert results[0].city == "Victoria"
    assert results[0].province == "BC"

    results = address_service.find(city="Victoria", province="AB")
    assert len(results) == 0

    results = address_service.find(city="Victoria", country="Australia")
    assert len(results) == 1
    assert results[0].country == "Australia"


# --- Schema & ID Management Tests ---
def test_schema_creation(fake_db):
    """Test that the database schema for the addresses table is created correctly."""
    cursor = fake_db.cursor()
    cursor.execute("PRAGMA table_info(addresses)")
    columns = cursor.fetchall()
    column_names = {col[1] for col in columns}  # Set for easier lookup

    expected_columns = {
        "id",
        "start",
        "end",
        "street",
        "city",
        "province",
        "country",
        "postal_code",
        "notes",
    }
    assert expected_columns.issubset(column_names)

    # Check primary key and NOT NULL for essential fields
    id_col = next(col for col in columns if col[1] == "id")
    assert id_col[5] == 1  # 5th element is 'pk' (1 for primary key)

    start_col = next(col for col in columns if col[1] == "start")
    assert start_col[3] == 1  # 3rd element is 'notnull' (1 for NOT NULL)


def test_id_auto_increment(address_service):
    """Test that IDs are auto-incrementing."""
    id1 = address_service.add(
        start="2024-01-01",
        street="1st St",
        city="City1",
        country="Country1",
        postal_code="P1",
    )
    id2 = address_service.add(
        start="2024-01-02",
        street="2nd St",
        city="City2",
        country="Country2",
        postal_code="P2",
    )
    id3 = address_service.add(
        start="2024-01-03",
        street="3rd St",
        city="City3",
        country="Country3",
        postal_code="P3",
    )
    assert id1 == 1
    assert id2 == 2
    assert id3 == 3


def test_id_reuse_after_deletion(address_service):
    """Test ID assignment behavior after deletions.
    SQLite's default INTEGER PRIMARY KEY reuses IDs if they are the highest available.
    If AUTOINCREMENT is used, IDs are never reused.
    This test assumes default INTEGER PRIMARY KEY behavior (IDs might be reused).
    """
    id1 = address_service.add(
        start="2025-01-01",
        street="A",
        city="B",
        country="C",
        postal_code="1",
    )
    id2 = address_service.add(
        start="2025-01-02",
        street="D",
        city="E",
        country="F",
        postal_code="2",
    )
    id3 = address_service.add(
        start="2025-01-03",
        street="G",
        city="H",
        country="I",
        postal_code="3",
    )

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3

    # Delete the address with id2
    address_service.delete(id=id2)
    assert len(address_service.list()) == 2

    # Add a new address - without AUTOINCREMENT, id2 might be reused if it was the highest.
    # With typical INTEGER PRIMARY KEY, SQLite will assign the next available ID which is often the max_rowid + 1.
    # So, typically, it would be 4, not 2, unless the table was empty.
    # However, for `INTEGER PRIMARY KEY` without `AUTOINCREMENT`, if `id2` (value 2) was the highest, it might be reused.
    # If `id3` (value 3) was the highest, then the next ID would be 4.
    # Let's verify it gets a new, higher ID, confirming `AUTOINCREMENT`-like behavior in practice.
    id_new = address_service.add(
        start="2025-01-04",
        street="J",
        city="K",
        country="L",
        postal_code="4",
    )
    assert id_new == 4  # Expecting next sequential ID, not reuse of 2


# --- Edge Case Tests ---
def test_notes_special_characters(address_service):
    """Test notes field with various special ASCII characters."""
    special_notes = "Notes!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
    address_service.add(
        start="2024-02-01",
        street="Special Str",
        city="Special City",
        country="Special Country",
        postal_code="S P E C",
        notes=special_notes,
    )
    address = address_service.get(1)
    assert address.notes == special_notes


def test_notes_unicode_characters(address_service):
    """Test notes field with Unicode characters (emojis, accented letters)."""
    unicode_notes = "Hello world! 👋 Привет мир! España. 日本語."
    address_service.add(
        start="2024-02-02",
        street="Unicode Str",
        city="Unicode City",
        country="Unicode Country",
        postal_code="U N I",
        notes=unicode_notes,
    )
    address = address_service.get(1)
    assert address.notes == unicode_notes