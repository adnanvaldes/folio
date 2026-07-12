import os


def _data_dir():
    xdg = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(xdg, "folio")


def _default_db_path():
    d = _data_dir()
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "folio.db")
