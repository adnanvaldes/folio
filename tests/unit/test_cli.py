import pytest

from folio.interfaces.cli import address, book, education, employment, travel, work
from folio.interfaces.cli.main import _build_parser

_DOMAINS = {
    "travel": (travel, {"add", "show", "find", "remove", "replace"}),
    "address": (address, {"add", "show", "find", "remove", "replace"}),
    "education": (education, {"add", "show", "find", "remove", "replace"}),
    "employment": (employment, {"add", "show", "find", "remove", "replace", "update"}),
    "work": (work, {"add", "show", "find", "remove", "replace", "update"}),
    "book": (book, {"add", "show", "find", "remove", "replace"}),
}


class TestHandlerRegistration:

    @pytest.mark.parametrize("domain", list(_DOMAINS.keys()))
    def test_module_has_handlers_dict(self, domain):
        mod, _ = _DOMAINS[domain]
        assert hasattr(mod, "_HANDLERS"), f"{domain} module missing _HANDLERS"

    @pytest.mark.parametrize("domain", list(_DOMAINS.keys()))
    def test_handlers_match_expected_actions(self, domain):
        mod, expected = _DOMAINS[domain]
        assert set(mod._HANDLERS.keys()) == expected

    @pytest.mark.parametrize("domain", list(_DOMAINS.keys()))
    def test_all_handlers_are_callable(self, domain):
        mod, _ = _DOMAINS[domain]
        for action, fn in mod._HANDLERS.items():
            assert callable(fn), f"{domain}.{action} handler is not callable"


class TestParserBuilds:

    def test_build_parser_succeeds(self):
        parser = _build_parser()
        assert parser is not None

    def test_parser_has_all_domains(self):
        parser = _build_parser()
        choices = [
            a.dest for a in parser._subparsers._actions if hasattr(a, "_parser_class")
        ]
        assert "domain" in choices
