import os
import tomllib

from folio.config import _default_db_path


def _config_dir():
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(xdg, "folio")


def _config_path(custom=None):
    if custom:
        return custom
    return os.path.join(_config_dir(), "config.toml")


def load(custom_path=None):
    path = _config_path(custom_path)
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        db_url = f"sqlite:///{_default_db_path()}"
        with open(path, "w") as f:
            f.write("[database]\n")
            f.write(f"url = '{db_url}'\n")
        return {"database": {"url": db_url}}
    with open(path, "rb") as f:
        return tomllib.load(f) or {}


def resolve_db_url(config, cli_db=None):
    """Return the full database URL/path."""
    if cli_db:
        return cli_db
    url = config.get("database", {}).get("url")
    if not url:
        return _default_db_path()
    return url


def resolve_backend(url: str) -> str:
    """Return 'postgres' or 'sqlite' based on URL scheme."""
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return "postgres"
    return "sqlite"



