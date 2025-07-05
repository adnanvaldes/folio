import pytest
from unittest.mock import Mock
from folio.models.models import Work
from folio.models.common import ValidationResult


@pytest.fixture
def sample_work_dict():
    """
    Sample Work data for testing
    """
    return {
        "id": 2,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "genre": "Fiction",
        "is_read": True,
    }


@pytest.fixture
def work_instance():
    """
    A Work instance with mocked dependencies injected
    """
    return Work(
        id=1,
        title="Test Book",
        author="Test Author",
        year=2025,
        genre="Test Genre",
        is_read=True,
    )
