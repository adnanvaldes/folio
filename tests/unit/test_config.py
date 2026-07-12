import os

from folio.interfaces.cli import config


class TestConfigLoad:

    def test_bare_filename_does_not_crash(self, tmp_path):
        path = str(tmp_path / "myconfig.toml")
        result = config.load(custom_path=path)
        assert "database" in result
        assert os.path.exists(path)

    def test_nested_relative_path(self, tmp_path):
        path = str(tmp_path / "subdir" / "config.toml")
        result = config.load(custom_path=path)
        assert "database" in result
        assert os.path.exists(path)

    def test_existing_config_is_read(self, tmp_path):
        path = tmp_path / "config.toml"
        path.write_text("[database]\nurl = 'sqlite:///test.db'\n")
        result = config.load(custom_path=str(path))
        assert result["database"]["url"] == "sqlite:///test.db"
