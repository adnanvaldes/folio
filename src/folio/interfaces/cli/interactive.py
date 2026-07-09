def prompt_field(label, current, parser=None):
    display = str(current) if current is not None else ""
    try:
        raw = input(f"  {label} [{display}]: ").strip()
    except EOFError:
        raise ValueError("Cancelled (EOF)")
    if not raw:
        return current
    if parser:
        return parser(raw)
    return raw


def confirm():
    try:
        raw = input("Apply? [Y/n]: ").strip().lower()
    except EOFError:
        return False
    if not raw:
        return True
    return raw in ("y", "yes")


def print_record(headers_values):
    for label, val in headers_values:
        display = str(val) if val is not None else ""
        print(f"  {label}: {display}")
