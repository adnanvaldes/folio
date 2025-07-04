import pytest
from unittest.mock import Mock
from folio.models.models import Work
from folio.models.common import ValidationResult

class TestWorkValidation:
    def test_validate_delegates_to_validator(self, work_instance):
        """
        Test that Work.validate() calls the injected validator
        """
        result = work_instance.validate()

        work_instance.validator.validate.assert_called_once_with(work_instance)
        assert result.is_valid is True

    def test_validate_with_validation_errors(self, work_instance):
        """
        Test validation failure
        """
        work_instance.validator.validate.return_value = ValidationResult(is_valid=False, errors=["Title too short"])
        result = work_instance.validate()

        assert result.is_valid is False
        assert "Title too short" in result.errors

class TestWorkSerialization:
    def test_validate_delegates_to_serializer(self, work_instance):
        """
        Test that Work.to_dict() calls the injected serializer
        """
        result = work_instance.to_dict()
        work_instance.serializer.to_dict.assert_called_once_with(work_instance)
        assert isinstance(result, dict)
