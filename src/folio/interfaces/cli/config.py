import os

import yaml

DEFAULT_CONFIG = {"database": {"url": "sqlite:///folio.db"}}


def _config_dir():
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(xdg, "folio")


def _config_path(custom=None):
    if custom:
        return custom
    return os.path.join(_config_dir(), "config.yaml")


def load(custom_path=None):
    path = _config_path(custom_path)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        return dict(DEFAULT_CONFIG)
    with open(path) as f:
        return yaml.safe_load(f) or {}


def db_path(config, cli_db=None):
    if cli_db:
        return cli_db
    url = config.get("database", {}).get("url", "sqlite:///folio.db")
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///") :]
    return url
