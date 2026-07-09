# AGENTS.md — Folio Project

## Overview

Folio is a personal record-keeping CLI app for tracking travel, addresses, employment, literary works, and books. Built to practice SOLID, GoF design patterns, and Clean Architecture (Cosmic Python). The result is over-engineered but usable and extensible.

```
folio [--config <path>] [--db <path>] [--json] <domain> <action> [args]
```

Domains: `travel`, `address`, `employment`, `work`, `book`
Actions: `add`, `list`, `find`, `remove`, `replace` (+ `update` for work, employment)

**Version:** 1.0.1 | **Python:** >=3.13 | **Deps:** pyyaml (config), black, mypy, pytest, ruff, pytest-cov (dev)

---

## Architecture (Clean Architecture)

```
folio (entry: folio.interfaces.cli.main:main)
  └── interfaces/cli/    ← adapters (argparse handlers)
  ├── models/            ← frozen dataclasses (entities)
  ├── services/          ← business logic (use cases)
  ├── repositories/      ← ABCs (base.py) + SQLite (sql/)
  └── uow/               ← Unit of Work ABC + SQLite impl
```

Each domain follows the same stack: **Model → Repository ABC → SQLite Repository → Service → Unit of Work → CLI handler**

---

## Models (src/folio/models/)

All are `@dataclasses.dataclass(frozen=True, eq=False)` with custom `__eq__`/`__hash__` via `_identity_fields()` and ordering via `_ordering_fields()`.

| Model | Identity Fields | Key Attributes |
|---|---|---|
| **Travel** | `origin, destination, date` | note |
| **Address** | `street, city, province(↓""), country, postal_code, start, end` | methods: `is_open`, `duration`, `overlaps()`, `close()`, `reopen()` |
| **Employment** | `company.lower(), start` | supervisor, address, phone, end |
| **Work** | `author.lower(), title.lower(), (is_none_year, year)` | genre, is_read |
| **Book** | `*Work.identity, format_type.value, isbn` | pages (print/ebook), duration_minutes (audio), narrator |

Identity matching rules:
- **Travel:** exact match (codes already uppercased in `__post_init__`)
- **Address:** case-insensitive text fields via `LOWER()`, NULLs via `IS NULL`
- **Employment:** case-insensitive company name
- **Work:** case-insensitive author/title; year uses sentinel `(None, year)` to distinguish NULL from same-int
- **Book:** delegates identity to parent Work + format_type + isbn

Additional types:
- **FormatType** (Enum): `PRINT`, `EBOOK`, `AUDIO`
- **TimelineDiff** (frozen dataclass): `to_add`, `to_remove`, `to_replace` tuples
- **`calculate_new_timeline()`** (function): conflict detection for address timeline (absorb, split, truncate_front, truncate_back)

---

## Design Patterns

| Pattern | Location | Description |
|---|---|---|
| **ABC / Interface** | `repositories/base.py`, `uow/unit_of_work.py` | 5 repository ABCs + 1 UoW ABC with `@abstractmethod` |
| **Repository** | `repositories/base.py` + `repositories/sql/` | Abstract repos + SQLite implementations |
| **Unit of Work** | `uow/unit_of_work.py` + `uow/sqlite/sqlite_uow.py` | Context manager, commit/rollback on `__exit__` |
| **Decorator** | `interfaces/cli/*.py` | `@handler("action")` registers into `_HANDLERS` dict |
| **Dependency Injection** | All services | Services receive `UnitOfWork` via constructor |
| **Template Method** | `uow/unit_of_work.py` | `__enter__` calls `_start()`, `__exit__` calls commit/rollback + `_cleanup()` |
| **Value Object** | `models/timeline.py` | `TimelineDiff` is an immutable result object |

---

## Import Conventions

All imports go through `__init__.py` re-exports (not deep module paths):

```python
from folio.models import Address, Book, Employment, Travel, Work
from folio.services import AddressService, BookService
from folio.uow import AddressSQLiteUoW, UnitOfWork
from folio.repositories import AddressRepository
```

Exception: files inside `models/` use relative imports (`.work import Work`) to avoid circular deps.

---

## CLI Handler Pattern

Each domain module in `interfaces/cli/` has:
- `setup(parser)` — registers action subparsers with arguments
- `_HANDLERS: dict[str, Callable]` — maps action → handler function
- `@handler("action")` decorator — registers into `_HANDLERS`

Identity fields are positional args; optional fields use `--flags`. `find` uses optional flags for all filters.

Handler built-in helpers:
- `_find_one(service, **kwargs)` — fetches exactly one record or raises ValueError
- `_interactive_replace(old)` — fallback when no `--new-*` flags provided
- `_parse_date(s)` — `dt.date.fromisoformat()`

Output via `print_item(obj, json_mode)` / `print_list(items, json_mode)`.

---

## Services

All services wrap operations in `with self.uow:` context manager:
- **TravelService** — CRUD passthrough to repo
- **AddressService** — timeline-aware add (uses `calculate_new_timeline`), safe remove (latest-open only), safe replace (no-overlap check)
- **EmploymentService** — CRUD + `update()` for non-identity fields
- **WorkService** — CRUD + `update()`; `remove(force=True)` cascades to books
- **BookService** — CRUD; `add()` auto-creates parent Work if not found

---

## Tests (433 total, ~0.3s runtime)

- **Unit tests** (`tests/unit/`): use `fake_uow` fixture (`FakeUnitOfWork` with in-memory fake repos)
- **Integration tests** (`tests/integration/`): use `fake_db` fixture (temp SQLite file, cleaned on teardown)
- **Fixtures** in `tests/conftest.py`: `FakeUnitOfWork` (tracks `committed` bool), `fake_db` (mkstemp + cleanup)
- **Fake repos** in `tests/fake_repositories.py`: in-memory `set` per domain, implement all ABC methods

---

## Commands

| Command | Purpose |
|---|---|
| `uv run pytest` | Run all tests |
| `uv run pytest --cov=folio --cov-report=term-missing` | Coverage report |
| `uv run black .` | Format code |
| `uv run ruff check src/ tests/` | Lint (rules: E, F, W, I, UP, SIM, N) |
| `uv run mypy src/` | Type-check (~32 expected `[attr-defined]` from UoW base class) |
| `uv run python -c "import folio; print(folio.__version__)"` | Check version |

---

## Current Git State

```
65fe2ac (HEAD -> main) chore: bump version to 1.0.1
4343e1e refactor(services): use typing.List for consistency with repositories
af04f01 refactor: use typing.List to avoid list() method name shadowing
66148c6 chore(deps): update uv.lock
270b411 docs: update README with installation instructions and CI workflow
86da4d1 chore(tests): update imports and formatting
ccdf7bd refactor: consolidate imports via __init__.py re-exports, add type annotations
d0a62eb fix(timeline): validate open-ended addresses in split/truncate operations
a0db51e feat(cli): add update action for employment and work
e45f5d3 feat: add XDG config dir, --version flag, bump version to 1.0.0
```

No tags. Branch `main`, up to date with `origin/main`.

---

## Future Goals / Possible Extensions

- TUI (Textual) or web interface as additional `interfaces/` adapters
- More output formats (CSV, YAML)
- Import/export functionality
- Statistics/reports (e.g., "countries visited per year")
- Additional filter operators (before, after, contains)
- Configurable ordering per domain
