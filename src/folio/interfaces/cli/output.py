import dataclasses
import datetime as dt
import json
from enum import Enum

from folio.models import Address, Book, Education, Employment, Travel, Work


def _obj_to_dict(obj):
    if isinstance(obj, dt.date):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        d = {}
        for field in obj.__dataclass_fields__:
            val = getattr(obj, field)
            if isinstance(val, dt.date):
                d[field] = val.isoformat()
            elif isinstance(val, Enum):
                d[field] = val.value
            elif dataclasses.is_dataclass(val) and not isinstance(val, type):
                d[field] = _obj_to_dict(val)
            else:
                d[field] = val
        return d
    return str(obj)


def _travel_rows(travels):
    rows = []
    for t in sorted(travels):
        rows.append([str(t.date), t.origin, t.destination, t.note])
    return ["Date", "Origin", "Destination", "Note"], rows


def _address_rows(addresses):
    rows = []
    for a in sorted(addresses):
        rows.append(
            [
                a.street,
                a.city,
                a.province or "",
                a.country,
                a.postal_code,
                str(a.start),
                str(a.end) if a.end else "Present",
            ]
        )
    return [
        "Street",
        "City",
        "Province",
        "Country",
        "Postal Code",
        "Start",
        "End",
    ], rows


def _employment_rows(employments):
    rows = []
    for e in sorted(employments):
        rows.append(
            [
                e.company,
                str(e.start),
                str(e.end) if e.end else "Present",
                e.supervisor,
                e.address,
                e.phone,
            ]
        )
    headers = ["Company", "Start", "End", "Supervisor", "Address", "Phone"]
    return headers, rows


def _education_rows(educations):
    rows = []
    for e in sorted(educations):
        rows.append(
            [
                e.field,
                str(e.start),
                str(e.end),
                e.school,
                e.city,
                e.country,
                e.credential,
            ]
        )
    return [
        "Field",
        "Start",
        "End",
        "School",
        "City",
        "Country",
        "Credential",
    ], rows


def _work_rows(works):
    rows = []
    for w in sorted(works):
        rows.append(
            [
                w.author,
                w.title,
                str(w.year) if w.year is not None else "",
                w.genre or "",
                "Yes" if w.is_read else "No",
            ]
        )
    return ["Author", "Title", "Year", "Genre", "Read"], rows


def _book_rows(books):
    rows = []
    for b in sorted(books):
        length = str(b.length) if b.length is not None else ""
        rows.append(
            [
                b.work.author,
                b.work.title,
                str(b.work.year) if b.work.year is not None else "",
                b.format_type.value,
                b.isbn or "",
                length,
                b.narrator or "",
            ]
        )
    return ["Author", "Title", "Year", "Format", "ISBN", "Length", "Narrator"], rows


_ROUTER = {
    Travel: _travel_rows,
    Address: _address_rows,
    Education: _education_rows,
    Employment: _employment_rows,
    Work: _work_rows,
    Book: _book_rows,
}


def print_list(items, json_output):
    if not items:
        return
    cls = type(items[0])
    if json_output:
        print(json.dumps([_obj_to_dict(i) for i in items], indent=2, default=str))
        return
    headers, rows = _ROUTER[cls](items)
    _print_table(headers, rows)


def print_domain_list(results, json_output):
    if json_output:
        out = {}
        for domain, items in results.items():
            out[domain] = [_obj_to_dict(i) for i in items]
        print(json.dumps(out, indent=2, default=str))
        return
    first = True
    for domain, items in results.items():
        if not items:
            continue
        if not first:
            print()
        first = False
        print(f"=== {domain.capitalize()} ===")
        print_list(items, json_output)


def print_item(item, json_output, label="Added"):
    if json_output:
        print(json.dumps(_obj_to_dict(item), indent=2, default=str))
    else:
        print(f"{label}: {item}")


def _print_table(headers, rows):
    col_count = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(col_count):
            widths[i] = max(widths[i], len(str(row[i])))
    sep = "  "
    line = sep.join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for row in rows:
        print(sep.join(str(c).ljust(w) for c, w in zip(row, widths)))
