from folio.exceptions import FolioInvalidFilterError

OPERATORS = {"before", "after", "contains"}

PG_RESERVED = {"end"}


def col(name: str) -> str:
    if name in PG_RESERVED:
        return f'"{name}"'
    return name


def parse_filter_key(key: str) -> tuple[str, str | None]:
    """Split 'field__op' into (field, op). No suffix returns (key, None)."""
    if "__" in key:
        base, op = key.rsplit("__", 1)
        if op not in OPERATORS:
            raise FolioInvalidFilterError(f"Unknown operator: '{op}'")
        return base, op
    return key, None


def validate_filter_fields(filters: dict, valid_fields: set[str]) -> None:
    """Validate filter keys (with operator suffixes stripped) against valid fields."""
    invalid = set()
    for key in filters:
        base, _op = parse_filter_key(key)
        if base not in valid_fields:
            invalid.add(key)
    if invalid:
        raise FolioInvalidFilterError(f"Invalid filter fields: {invalid}")


def build_where_clause(params: dict, placeholder: str = ":{field}") -> str:
    parts = []
    for field, value in params.items():
        if value is None:
            parts.append(f"{col(field)} IS NULL")
        else:
            parts.append(f"{col(field)} = {placeholder.format(field=field)}")
    return " AND ".join(parts)
