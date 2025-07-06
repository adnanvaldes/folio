import json
import pytest
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from folio.services.serializers import DictSerializer, JSONSerializer


@dataclass
class SampleRecord:
    """
    A test Record class that contains generic fields
    """

    int_field: int
    string_field: str
    bool_field: bool
    float_field: float


@dataclass
class SingleFieldSampleRecord:
    value: str


@dataclass
class ComplexSampleRecord:
    """
    A more complex Record with different data structures
    """

    list_field: List[str]
    dict_field: Dict[str, Any]
    none_default_field: Optional[float] = None


@dataclass
class EmptySampleRecord:
    pass


class TestDictSerializer:
    """Test cases for DictSerializer"""

    def setup_method(self):
        self.serializer = DictSerializer()
        self.sample_record = SampleRecord(
            int_field=1, string_field="a string", bool_field=False, float_field=2.0
        )
        self.sample_dict = {
            "int_field": 1,
            "string_field": "a string",
            "bool_field": False,
            "float_field": 2.0,
        }
        self.sample_record_complex = ComplexSampleRecord(
            list_field=["a", "b", "c"],
            dict_field={"a": 1, "b": "some string", "c": ["a list"]},
        )
        self.sample_complex_dict = {
            "list_field": ["a", "b", "c"],
            "dict_field": {"a": 1, "b": "some string", "c": ["a list"]},
            "none_default_field": None,
        }

    # Serialization tests

    def test_serialize_simple_record(self):
        result = self.serializer.serialize(self.sample_record)

        assert isinstance(result, dict)
        assert result == self.sample_dict

    def test_serialize_with_none_values(self):
        record = SampleRecord(
            int_field=2, string_field="test2", bool_field=True, float_field=None
        )
        result = self.serializer.serialize(record)
        expected = {
            "int_field": 2,
            "string_field": "test2",
            "bool_field": True,
            "float_field": None,
        }
        assert result == expected

    def test_serialize_complex_record(self):
        result = self.serializer.serialize(self.sample_record_complex)
        assert result == self.sample_complex_dict

    def test_serialize_empty_record(self):
        record = EmptySampleRecord()
        result = self.serializer.serialize(record)
        assert result == {}

    # Deserialization tests

    def test_deserialize_simple_record(self):
        result = self.serializer.deserialize(self.sample_dict, SampleRecord)

        assert isinstance(result, SampleRecord)
        assert result == self.sample_record

    def test_deserialize_with_none_values(self):
        data = {
            "int_field": 2,
            "string_field": "test2",
            "bool_field": True,
            "float_field": None,
        }
        record = SampleRecord(
            int_field=2, string_field="test2", bool_field=True, float_field=None
        )
        result = self.serializer.deserialize(data, SampleRecord)

        assert isinstance(result, SampleRecord)
        assert result == record

    def test_deserialize_complex_record(self):
        result = self.serializer.deserialize(
            self.sample_complex_dict, ComplexSampleRecord
        )
        assert isinstance(result, ComplexSampleRecord)
        assert result == self.sample_record_complex

    def test_deserialize_ignore_extra_fields(self):
        data = {
            "int_field": 2,
            "string_field": "test2",
            "bool_field": True,
            "float_field": None,
            "extra_field": "extra data",
        }

        # TODO when serializer implementation is complete
        with pytest.raises(TypeError):
            result = self.serializer.deserialize(data, SampleRecord)
            assert result == self.sample_record

    def test_deserialize_empty_record(self):
        result = self.serializer.deserialize({}, EmptySampleRecord)
        assert result == EmptySampleRecord()

    def test_round_trip_serialization(self):
        serialized = self.serializer.serialize(self.sample_record)

        deserialized = self.serializer.deserialize(serialized, SampleRecord)

        assert deserialized == self.sample_record
