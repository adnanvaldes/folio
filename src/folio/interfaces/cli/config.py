import os
import tomllib


def _data_dir():
    xdg = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(xdg, "folio")


def _default_db_path():
    d = _data_dir()
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "folio.db")


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
        os.makedirs(os.path.dirname(path), exist_ok=True)
        db_url = f"sqlite:///{_default_db_path()}"
        with open(path, "w") as f:
            f.write("[database]\n")
            f.write(f'url = "{db_url}"\n')
        return {"database": {"url": db_url}}
    with open(path, "rb") as f:
        return tomllib.load(f) or {}


def db_path(config, cli_db=None):
    if cli_db:
        return cli_db
    url = config.get("database", {}).get("url")
    if not url:
        return _default_db_path()
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///") :]
    return url
