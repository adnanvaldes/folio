import json
import pytest
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from serializer_data import expected_data
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


class SerializerBaseTest:

    def setup_method(self):
        self.serializer = self.serializer_class()
        self.sample_record = SampleRecord(
            int_field=1, string_field="a string", bool_field=False, float_field=2.0
        )
        self.sample_record_complex = ComplexSampleRecord(
            list_field=["a", "b", "c"],
            dict_field={"a": 1, "b": "some string", "c": ["a list"]},
        )

    def get_expected(self, key):
        return expected_data[self.format_name][key]

    # Serialization tests

    def test_serialize_simple_record(self):
        result = self.serializer.serialize(self.sample_record)

        assert isinstance(result, self.output_type)
        assert result == self.get_expected("simple")

    def test_serialize_with_none_values(self):
        record = SampleRecord(
            int_field=2, string_field="test2", bool_field=True, float_field=None
        )
        result = self.serializer.serialize(record)
        assert result == self.get_expected("with_none")

    def test_serialize_complex_record(self):
        result = self.serializer.serialize(self.sample_record_complex)
        assert result == self.get_expected("complex")

    def test_serialize_empty_record(self):
        record = EmptySampleRecord()
        result = self.serializer.serialize(record)
        assert result == self.get_expected("empty")

    # Deserialization tests

    def test_deserialize_simple_record(self):
        result = self.serializer.deserialize(self.get_expected("simple"), SampleRecord)

        assert isinstance(result, SampleRecord)
        assert result == self.sample_record

    def test_deserialize_with_none_values(self):
        expected = SampleRecord(
            int_field=2, string_field="test2", bool_field=True, float_field=None
        )
        result = self.serializer.deserialize(
            self.get_expected("with_none"), SampleRecord
        )

        assert isinstance(result, SampleRecord)
        assert result == expected

    def test_deserialize_complex_record(self):
        result = self.serializer.deserialize(
            self.get_expected("complex"), ComplexSampleRecord
        )
        assert isinstance(result, ComplexSampleRecord)
        assert result == self.sample_record_complex

    def test_deserialize_ignore_extra_fields(self):
        # TODO when serializer implementation is complete
        with pytest.raises(TypeError):
            result = self.serializer.deserialize(
                self.get_expected("extra"), SampleRecord
            )

    def test_deserialize_empty_record(self):
        result = self.serializer.deserialize(
            self.get_expected("empty"), EmptySampleRecord
        )
        assert result == EmptySampleRecord()

    def test_round_trip_serialization(self):
        serialized = self.serializer.serialize(self.sample_record)

        deserialized = self.serializer.deserialize(serialized, SampleRecord)

        assert deserialized == self.sample_record


class TestDictSerializer(SerializerBaseTest):

    serializer_class = DictSerializer
    format_name = "dict"
    output_type = dict


class TestJSONSerializer(SerializerBaseTest):
    serializer_class = JSONSerializer
    format_name = "json"
    output_type = str
