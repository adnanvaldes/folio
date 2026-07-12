# AGENTS.md — Folio Project

## Overview

Folio is a personal record-keeping CLI app for tracking travel, addresses, education, employment, literary works, and books. Built to practice SOLID, GoF design patterns, and Clean Architecture (Cosmic Python). The result is over-engineered but usable and extensible.

```
folio [--config <path>] [--db <path>] [--json] <domain> <action> [args]
```

Domains: `travel`, `address`, `education`, `employment`, `work`, `book`
Actions: `add`, `list`, `find`, `remove`, `replace` (+ `update` for work, employment)

**Version:** 1.1.0 | **Python:** >=3.14 | **Deps:** none (stdlib only) | **Optional:** `psycopg[binary]>=3.3` (`pip install folio[postgres]`) | **Dev:** black, mypy, pytest, ruff, pytest-cov

---

## Architecture (Clean Architecture)

```
folio (entry: folio.interfaces.cli.main:main)
├── config.py            ← shared config (_default_db_path)
├── exceptions.py        ← domain exception hierarchy
├── interfaces/cli/      ← adapters (argparse handlers + UoW factories)
├── models/              ← frozen dataclasses (entities)
├── services/            ← business logic (use cases)
├── repositories/        ← ABCs (base.py) + SQL implementations
│   └── sql/
│       ├── _filters.py  ← shared filter helpers (parse_filter_key, build_where_clause, col, etc.)
│       ├── sqlite/      ← SQLite repositories
│       └── postgres/    ← PostgreSQL repositories
└── uow/                 ← Unit of Work ABC + SQLite impl + PostgreSQL impl
    ├── sqlite/
    └── postgres/
```

Each domain follows the same stack: **Model → Repository ABC → SQL Repository → Service → Unit of Work → CLI handler**

Backends are selected automatically via URL scheme:
- `sqlite:///path/to/db` or bare path → SQLite (default)
- `postgresql://...` or `postgres://...` → PostgreSQL

---

## Models (src/folio/models/)

All are `@dataclasses.dataclass(frozen=True, eq=False)` with custom `__eq__`/`__hash__` via `_identity_fields()` and ordering via `_ordering_fields()`.

| Model | Identity Fields | Key Attributes |
|---|---|---|
| **Travel** | `origin, destination, date` | note |
| **Address** | `street, city, province(↓""), country, postal_code, start, end` | methods: `is_open`, `duration`, `overlaps()`, `close()`, `reopen()` |
| **Education** | `field.lower(), start, end, school.lower(), city.lower(), country.lower(), credential.lower()` | `duration` property |
| **Employment** | `company.lower(), start` | supervisor, address, phone, end |
| **Work** | `author.lower(), title.lower(), (is_none_year, year)` | genre, is_read |
| **Book** | `*Work.identity, format_type.value, isbn` | pages (print/ebook), duration_minutes (audio), narrator |

Identity matching rules:
- **Travel:** case-insensitive via `LOWER()` (codes already uppercased in `__post_init__`)
- **Address:** case-insensitive text fields via `LOWER()` / `ILIKE`, NULLs via `IS NULL`
- **Education:** case-insensitive text fields; all 7 fields are required and identity
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
| **ABC / Interface** | `repositories/base.py`, `uow/unit_of_work.py` | 6 repository ABCs + 1 UoW ABC with `@abstractmethod` |
| **Repository** | `repositories/base.py` + `repositories/sql/` | Abstract repos + SQLite + PostgreSQL implementations |
| **Unit of Work** | `uow/unit_of_work.py` + `uow/sqlite/` + `uow/postgres/` | Context manager, commit/rollback on `__exit__` |
| **Factory** | `interfaces/cli/common.py` | `make_*_uow(db_url)` selects SQLite or PostgreSQL UoW by URL scheme |
| **Decorator** | `interfaces/cli/*.py` | `@handler("action")` registers into `_HANDLERS` dict |
| **Dependency Injection** | All services | Services receive `UnitOfWork` via constructor |
| **Template Method** | `uow/unit_of_work.py` | `__enter__` calls `_start()`, `__exit__` calls commit/rollback + `_cleanup()` |
| **Value Object** | `models/timeline.py` | `TimelineDiff` is an immutable result object |

---

## Import Conventions

All imports go through `__init__.py` re-exports (not deep module paths):

```python
from folio.config import _default_db_path
from folio.models import Address, Book, Education, Employment, Travel, Work
from folio.repositories import (
    AddressRepository, PgAddressRepository, SQLiteAddressRepository,
)
from folio.repositories.sql import build_where_clause, col, parse_filter_key, validate_filter_fields
from folio.services import AddressService, BookService, EducationService
from folio.uow import UnitOfWork
```

Exception: files inside `models/` use relative imports (`.work import Work`) to avoid circular deps.
Exception: files within the same package use relative imports for siblings (e.g., `from .work_repository import _work_identity_where`).
Exception: `_default_db_path` lives in `folio/config.py` (shared) so both `uow/` and `interfaces/cli/` can import it without cross-layer violations.
Exception: PostgreSQL UoW classes are imported lazily inside `common.py` `_load_uows()` to avoid loading psycopg when using SQLite. Both SQLite and PG UoW classes are loaded via a single lazy `_load_uows(db_url)` call, keyed by domain name.

---

## Backends

### SQLite (default, zero dependencies)

- Connection: `sqlite3.connect(path)`
- Dates stored as `TEXT` (ISO strings), booleans as `INTEGER CHECK(0,1)`
- Param style: `:name`
- Case-insensitive matching: `LOWER(x) = LOWER(y)`
- Auto-increment: `INTEGER PRIMARY KEY AUTOINCREMENT`
- Files: `repositories/sql/sqlite/*.py`, `uow/sqlite/sqlite_uow.py`

### PostgreSQL (optional, requires `pip install folio[postgres]`)

- Connection: `psycopg.connect(dsn)` with `dict_row` factory
- Native `DATE` and `BOOLEAN` column types (no conversion needed)
- Param style: `%(name)s`
- Case-insensitive matching: `ILIKE`
- Auto-increment: `SERIAL PRIMARY KEY`
- psycopg imported eagerly in `postgres_uow.py` and PG repo modules, but only loaded when PG backend is selected (lazy import in `common.py` `_load_uows()`)
- `uow/__init__.py` does NOT import PG classes — only SQLite UoW + UnitOfWork
- Reserved keywords (e.g. `end`) are double-quoted via `col()` helper from `_filters.py`
- Files: `repositories/sql/postgres/*.py`, `uow/postgres/postgres_uow.py`

### Config

Shared configuration in `folio/config.py`:
- `_data_dir()` — XDG data directory (`~/.local/share/folio`)
- `_default_db_path()` — default SQLite database path

CLI-specific config in `interfaces/cli/config.py`:
- `load()` — loads `~/.config/folio/config.toml`
- `resolve_db_url()` — resolves database URL from config + CLI flags
- `resolve_backend()` — returns `"postgres"` or `"sqlite"` from URL scheme

Config file (`~/.config/folio/config.toml`):

```toml
[database]
# SQLite (default)
url = "sqlite:///path/to/folio.db"

# PostgreSQL
url = "postgresql://user:pass@host:5432/folio"
```

The `--db` CLI flag overrides the config file. Backend is auto-detected from URL scheme.

---

## CLI Handler Pattern

Each domain module in `interfaces/cli/` has:
- `setup(parser)` — registers action subparsers with arguments
- `_HANDLERS: dict[str, Callable]` — maps action → handler function
- `@handler("action")` decorator — registers into `_HANDLERS`

Identity fields are positional args; optional fields use `--flags`. `find` uses optional flags for all filters, plus `--before`, `--after`, `--contains` for operator-based search.

Handler built-in helpers:
- `_find_one(service, **kwargs)` — fetches exactly one record or raises `FolioNotFoundError`/`FolioAmbiguousQueryError`
- `_interactive_replace(old)` — fallback when no `--new-*` flags provided
- `_parse_date(s)` — `dt.date.fromisoformat()`

UoW factory helpers (in `common.py`):
- `make_travel_uow(db_url)`, `make_address_uow(db_url)`, etc. — returns SQLite or PostgreSQL UoW based on URL scheme

Output via `print_item(obj, json_mode)` / `print_list(items, json_mode)`.

---

## Services

All services wrap operations in `with self.uow:` context manager:
- **TravelService** — CRUD passthrough to repo
- **AddressService** — timeline-aware add (uses `calculate_new_timeline`), safe remove (latest-open only), safe replace (no-overlap check)
- **EducationService** — CRUD passthrough to repo (no `update()`; all fields are identity)
- **EmploymentService** — CRUD + `update()` for non-identity fields
- **WorkService** — CRUD + `update()`; `remove(force=True)` cascades to books
- **BookService** — CRUD; `add()` auto-creates parent Work if not found

---

## Tests (607 passed, ~1.7s runtime with PG, ~0.5s without)

- **Unit tests** (`tests/unit/`): use `fake_uow` fixture (`FakeUnitOfWork` with in-memory fake repos)
- **SQLite integration tests** (`tests/integration/`): use `fake_db` fixture (temp SQLite file, cleaned on teardown)
- **PostgreSQL integration tests** (`tests/integration/test_pg_*.py`): use `pg_conn` fixture, require `FOLIO_PG_DSN` env var
- **Fixtures** in `tests/conftest.py`: `FakeUnitOfWork` (tracks `committed` bool), `fake_db` (mkstemp + cleanup)
- **PG fixtures** in `tests/integration/conftest.py`: `pg_conn` (live connection, auto-rollback), `_pg_drop_tables` (autouse, drops tables for isolation)
- **Fake repos** in `tests/fake_repositories.py`: in-memory `set` per domain, implement all ABC methods
- **PG tests (82 total):** `test_pg_{travel,address,work,book,employment,education}_repository.py`

---

## Commands

| Command | Purpose |
|---|---|
| `uv run pytest` | Run all tests (PG tests auto-skip without `FOLIO_PG_DSN`) |
| `uv run pytest --cov=folio --cov-report=term-missing` | Coverage report |
| `uv run black .` | Format code |
| `uv run ruff check src/ tests/` | Lint (rules: E, F, W, I, UP, SIM, N) |
| `uv run mypy src/` | Type-check (0 errors across 54 source files) |
| `uv run python -c "import folio; print(folio.__version__)"` | Check version |
| `FOLIO_PG_DSN="postgresql://..." uv run pytest tests/integration/test_pg_*` | Run PG integration tests |

---

## Current Git State

```
cd5c58a (HEAD -> main) Merge branch 'main' of github.com:adnanvaldes/folio actions: update ci permissions
11c900a Potential fix for code scanning alert no. 1: Workflow does not contain permissions
8c24c55 feat(services): one-directional upgrade of is_read and genre on book add
162b8c7 fix(cli): use found record fields in travel replace fallback instead of raw args
154b2fb fix(models): skip zero-length address pieces in timeline SPLIT and TRUNCATE_BACK
70c1fe2 fix(cli): guard os.makedirs against empty dirname for relative --config paths
e1bd5fa chore: format source code with black
b17790b refactor(models): drop frozen=True, replace object.__setattr__ with direct assignment
fb9eec8 refactor(cli): replace hasattr duck-typing with dataclasses.is_dataclass() in output
ce12582 refactor(repos): extract build_where_clause to _filters.py, remove 5 duplicate _where_clause methods
```

No tags. Branch `main` after history rewrite.

**Uncommitted changes:** PostgreSQL backend, repo directory restructuring, import cleanup, lazy UoW imports, PG reserved keyword quoting. Run `git status` to see full diff.

---

## Next Steps / Roadmap

### Immediate
- **Commit PostgreSQL backend** — stage all changes, write commit message, optionally tag and release v1.2.0
- **Release workflow** — `.github/workflows/release.yml` to auto-build and publish on tag push

### Features
- **ISBN-less multi-copy support** — deliberate design needed for books without ISBNs (currently `add()` raises on any duplicate)
- **Import/export** — CSV and/or YAML import/export for bulk loading and migration
- **Stats command** — e.g., `folio travel stats` with "countries visited per year", most-traveled routes, etc.
- **Configurable ordering** — `--sort-by` flag or config option per domain

### Architecture
- **TUI with Textual** — second `interfaces/` adapter, reusing existing services/repos unchanged
- **Web interface** — FastAPI or similar as another adapter

### Polish
- **Better test coverage** — add CLI handler tests, edge cases in timeline/ISBN validation

---

## Recent Changes

| Change | Files | Description |
|---|---|---|
| **Lazy UoW imports** | `uow/__init__.py`, `interfaces/cli/common.py` | Removed PG UoW imports from `uow/__init__.py`; both SQLite and PG UoW classes are now loaded lazily via a single `_load_uows(db_url)` function in `common.py`, avoiding psycopg import when using SQLite. |
| **PG reserved keyword quoting** | `repositories/sql/_filters.py`, `repositories/sql/__init__.py`, `repositories/sql/postgres/address_repository.py`, `postgres/education_repository.py`, `postgres/employment_repository.py` | Added `col()` helper that double-quotes PostgreSQL reserved keywords (e.g. `"end"`) in identifier positions. Applied across all PG repos and `build_where_clause`. |
| **Fixed invalid ISBN in PG tests** | `tests/integration/test_pg_book_repository.py` | Replaced `978-0451524936` (bad checksum) with `9780000000026` to match SQLite tests. |
| **Import cleanup** | 24 files across `repositories/`, `uow/`, `interfaces/cli/`, `tests/` | Moved imports to top of file, eliminated lazy imports, added `sql/__init__.py` re-exporting filter helpers, renamed repo files to drop `sqlite_`/`pg_` prefixes, fixed all imports to use `__init__.py` re-exports, moved `_default_db_path` to shared `folio/config.py`. |
| **Repo directory restructure** | `repositories/sql/` | Created symmetric `sqlite/` and `postgres/` subdirectories with `__init__.py` re-exports. Deleted duplicate `postgres/_filters.py` — shared `_filters.py` now handles both via `placeholder` parameter. |
| **PostgreSQL backend** | `repositories/sql/postgres/`, `uow/postgres/`, `interfaces/cli/common.py`, `interfaces/cli/config.py`, all 6 CLI handlers, 6 PG test files, `pyproject.toml` | Full PostgreSQL backend with 6 repositories, 6 UoW classes, URL-based backend selection via factory functions, `%(name)s` param style, native DATE/BOOLEAN, ILIKE case-insensitive matching. Optional dep: `psycopg[binary]>=3.3`. 82 integration tests gated behind `FOLIO_PG_DSN`. |
| **Filter operators on find** | `repositories/sql/_filters.py`, all 6 repos, all 6 CLI handlers | Added `__before`, `__after`, `__contains` operator suffixes in filter keys, backed by CLI flags `--before`, `--after`, `--contains` on all `find` subcommands. |
| **Domain-specific exceptions** | `exceptions.py`, all models/repos/services/CLI | Replaced 99 bare `ValueError` raises with 10 typed exceptions under `FolioError` hierarchy. main.py catches `FolioError`. |
| **mypy: UoW property declarations** | `uow/unit_of_work.py`, `uow/sqlite/sqlite_uow.py`, `tests/conftest.py` | Added 6 `@property` on UnitOfWork ABC; concrete UoW and FakeUnitOfWork use `self._attr` private attributes. mypy: 37 → 0 errors. |
| **Work field normalization** | `models/work.py` | `__post_init__` now strips author/title via `object.__setattr__`, matching Address/Employment/Travel. Prevents SQL lookup failures on whitespace-padded inputs. |
| **Address CLI find-then-mutate** | `interfaces/cli/address.py` | `_remove` and `_replace` now use `_find_one()` to fetch the DB-hydrated record first, preventing race conditions between domain equality (case-insensitive) and SQLite DELETE/UPDATE (exact-case). |
| **Open-address overlap guard** | `models/timeline.py` | Narrowed from broad `not existing.is_open or existing.start >= new.start` to `kind is _OverlapKind.ABSORB`. TRUNCATE_BACK now falls through to `needs_confirmation` as intended. |
| **Identity logic consolidation** | `repositories/sql/sqlite/work_repository.py` + `sqlite/book_repository.py` | Extracted `_work_identity_where()` helper; both `SQLiteWorkRepository.find()` and `SQLiteBookRepository._lookup_work_id()` use it. |
| **list() → list_all() rename** | all repos, services, CLI handlers, tests | Renamed to eliminate method-name shadowing with builtin `list` type; dropped `typing.List` in favor of builtin `list[X]`, resolving 53 ruff violations. |
| **main() exception widening** | `interfaces/cli/main.py` | Now catches `TypeError` alongside `ValueError` for friendly error output. |
| **Travel find case-insensitivity** | `repositories/sql/sqlite/travel_repository.py` | `find()` now uses `LOWER()` on origin/destination, matching Address/Education repos. |
| **Work/Employment update WHERE** | `repositories/sql/sqlite/work_repository.py`, `sqlite/employment_repository.py` | `update()` WHERE clause narrowed to identity fields only (author/title/year for Work, company/start for Employment) — no longer includes non-identity fields that could cause stale-object `FolioNotFoundError`. |
| **ValueError catch** | `interfaces/cli/main.py` | Added `ValueError` to caught exceptions so bad user input (e.g. invalid dates) shows a friendly error instead of a traceback. |
| **Employment.__str__ safety** | `models/employment.py` | `__str__` now wraps `self.duration` in try/except to handle future-dated open-ended records. |
| **Work genre stripping** | `models/work.py` | `genre` field is now stripped in `__post_init__`, consistent with all other string fields across models. |
| **Book shared UoW** | `interfaces/cli/book.py` | `_remove` and `_replace` now share one `BookSQLiteUoW` between `WorkService` and `BookService` instead of creating two independent instances. |
