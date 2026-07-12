import pytest

from folio.exceptions import FolioInvalidFilterError
from folio.repositories.sql import (
    OPERATORS,
    parse_filter_key,
    validate_filter_fields,
)


class TestParseFilterKey:
    def test_plain_key(self):
        assert parse_filter_key("author") == ("author", None)

    def test_before_operator(self):
        assert parse_filter_key("start__before") == ("start", "before")

    def test_after_operator(self):
        assert parse_filter_key("date__after") == ("date", "after")

    def test_contains_operator(self):
        assert parse_filter_key("title__contains") == ("title", "contains")

    def test_invalid_operator(self):
        with pytest.raises(FolioInvalidFilterError, match="Unknown operator"):
            parse_filter_key("author__bogus")

    def test_operators_constant(self):
        assert {"before", "after", "contains"} == OPERATORS


class TestValidateFilterFields:
    def test_valid_plain_fields(self):
        validate_filter_fields(
            {"author": "Orwell", "title": "1984"}, {"author", "title", "year"}
        )

    def test_valid_operator_fields(self):
        validate_filter_fields(
            {"author__contains": "or", "year__before": 1950},
            {"author", "title", "year"},
        )

    def test_invalid_field(self):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            validate_filter_fields({"bogus": "value"}, {"author", "title"})

    def test_invalid_field_with_operator(self):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            validate_filter_fields({"bogus__contains": "val"}, {"author", "title"})

    def test_empty_filters(self):
        validate_filter_fields({}, {"author", "title"})
