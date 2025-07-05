import pytest
import json
from unittest.mock import Mock

from folio.models.models import Work
from folio.services.serializers import DictSerializer, JSONSerializer


class TestWorkInstantiation:
    """
    Test basic Work instantiation with different properties
    """

    def test_work_creation_optional_fields(self):
        work = Work(
            id=None,
            title="Test Book",
            author="Test Author",
            year=None,
            genre=None,
            is_read=False,
        )

        assert work.id is None
        assert work.year is None
        assert work.genre is None
        assert work.is_read is False


class TestWorkSerialization:
    def test_serialize_to_dict(self, work_instance):
        """
        Test serialization of Work with DictSerializer
        """
        result = work_instance.serialize(DictSerializer())

        assert isinstance(result, dict)
        assert result["title"] == "The Great Gatsby"
        assert result["is_read"] is True

    def test_serialize_to_json(self, work_instance):
        """
        Test serialization of Work with JSONSerializer
        """
        result = work_instance.serialize(JSONSerializer())

        assert isinstance(result, str)
        assert '"title": "The Great Gatsby"' in result
        assert '"is_read": true' in result

    def test_deserialize_from_dict(self, sample_work_dict):
        """
        Test deserialization into Work from dict
        """
        work = Work.deserialize(sample_work_dict, DictSerializer())

        assert isinstance(work, Work)
        assert work.title == "The Great Gatsby"
        assert work.is_read is True

    def test_deserialize_from_JSON(self, sample_work_dict):
        json_data = json.dumps(sample_work_dict)
        work = Work.deserialize(json_data, JSONSerializer())

        assert isinstance(work, Work)
        assert work.title == "The Great Gatsby"
        assert work.is_read is True
