import pytest
from unittest.mock import Mock
from folio.models.models import Work
from folio.models.common import ValidationResult

@pytest.fixture
def mock_validator():
    """
    Mock validator that always validates the result as valid
    """
    validator = Mock()
    validator.validate.return_value = ValidationResult(is_valid=True, errors=[])
    return validator

@pytest.fixture
def mock_serializer():
    """
    Mock serializer that returns a generic serialized Work dict 
    """
    serializer = Mock()
    serializer.to_dict.return_value = {
        "id" : 1,
        "title" : "Test Book",
        "author" : "Test Author",
        "year" : 2025,
        "genre" : "Test Genre",
        "is_read" : True
    }
    return serializer

@pytest.fixture
def mock_formatter():
    """
    Mock formatter #TODO
    """
    return Mock()

@pytest.fixture
def work_instance(mock_validator, mock_serializer, mock_formatter):
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
        validator=mock_validator,
        serializer=mock_serializer,
        formatter=mock_formatter
    )
