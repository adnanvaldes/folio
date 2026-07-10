# AGENTS.md — Folio Project

## Overview

Folio is a personal record-keeping CLI app for tracking travel, addresses, education, employment, literary works, and books. Built to practice SOLID, GoF design patterns, and Clean Architecture (Cosmic Python). The result is over-engineered but usable and extensible.

```
folio [--config <path>] [--db <path>] [--json] <domain> <action> [args]
```

Domains: `travel`, `address`, `education`, `employment`, `work`, `book`
Actions: `add`, `list`, `find`, `remove`, `replace` (+ `update` for work, employment)

**Version:** 1.1.0 | **Python:** >=3.13 | **Deps:** none (stdlib only) | **Dev:** black, mypy, pytest, ruff, pytest-cov

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
| **Education** | `field.lower(), start, end, school.lower(), city.lower(), country.lower(), credential.lower()` | `duration` property |
| **Employment** | `company.lower(), start` | supervisor, address, phone, end |
| **Work** | `author.lower(), title.lower(), (is_none_year, year)` | genre, is_read |
| **Book** | `*Work.identity, format_type.value, isbn` | pages (print/ebook), duration_minutes (audio), narrator |

Identity matching rules:
- **Travel:** case-insensitive via `LOWER()` (codes already uppercased in `__post_init__`)
- **Address:** case-insensitive text fields via `LOWER()`, NULLs via `IS NULL`
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
from folio.models import Address, Book, Education, Employment, Travel, Work
from folio.services import AddressService, BookService, EducationService
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

Identity fields are positional args; optional fields use `--flags`. `find` uses optional flags for all filters, plus `--before`, `--after`, `--contains` for operator-based search.

Handler built-in helpers:
- `_find_one(service, **kwargs)` — fetches exactly one record or raises `FolioNotFoundError`/`FolioAmbiguousQueryError`
- `_interactive_replace(old)` — fallback when no `--new-*` flags provided
- `_parse_date(s)` — `dt.date.fromisoformat()`

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

## Tests (533 total, ~0.4s runtime)

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
| `uv run mypy src/` | Type-check (0 errors across 41 source files) |
| `uv run python -c "import folio; print(folio.__version__)"` | Check version |

---

## Current Git State

```
82b8fb1 (HEAD -> main) docs: update AGENTS.md for current state
1b17fa0 feat: add filter operators to find across all domains
db87299 refactor: replace bare ValueError with domain-specific exceptions
166fa1c refactor(uow): declare repository properties on UnitOfWork ABC
43f178a refactor(models): remove redundant .strip() in _identity_fields/_ordering_fields
d0d541a fix(test): add case-insensitive matching to FakeAddressRepository and FakeWorkRepository find()
39799f9 docs: update AGENTS.md for education domain
a2ad07f test(education): add unit and integration tests
10d47f1 feat(education): add full domain stack
c020735 update config to use single quotes
```

No tags. Branch `main` after history rewrite.

---

## Next Steps / Roadmap

### Immediate
- **Release v1.1.0** — `git tag v1.1.0 && git push origin v1.1.0 && gh release create v1.1.0 --generate-notes`
- **Add release workflow** — `.github/workflows/release.yml` to auto-build and publish on tag push

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

## Recent Fixes

| Fix | Files | Description |
|---|---|---|
| **Filter operators on find** | `repositories/sql/_filters.py`, all 6 repos, all 6 CLI handlers | Added `__before`, `__after`, `__contains` operator suffixes in filter keys, backed by CLI flags `--before`, `--after`, `--contains` on all `find` subcommands. |
| **Domain-specific exceptions** | `exceptions.py`, all models/repos/services/CLI | Replaced 99 bare `ValueError` raises with 10 typed exceptions under `FolioError` hierarchy. main.py catches `FolioError`. |
| **mypy: UoW property declarations** | `uow/unit_of_work.py`, `uow/sqlite/sqlite_uow.py`, `tests/conftest.py` | Added 6 `@property` on UnitOfWork ABC; concrete UoW and FakeUnitOfWork use `self._attr` private attributes. mypy: 37 → 0 errors. |
| **Work field normalization** | `models/work.py` | `__post_init__` now strips author/title via `object.__setattr__`, matching Address/Employment/Travel. Prevents SQL lookup failures on whitespace-padded inputs. |
| **Address CLI find-then-mutate** | `interfaces/cli/address.py` | `_remove` and `_replace` now use `_find_one()` to fetch the DB-hydrated record first, preventing race conditions between domain equality (case-insensitive) and SQLite DELETE/UPDATE (exact-case). |
| **Open-address overlap guard** | `models/timeline.py` | Narrowed from broad `not existing.is_open or existing.start >= new.start` to `kind is _OverlapKind.ABSORB`. TRUNCATE_BACK now falls through to `needs_confirmation` as intended. |
| **Identity logic consolidation** | `repositories/sql/sqlite_work_repository.py` + `sqlite_book_repository.py` | Extracted `_work_identity_where()` helper; both `SQLiteWorkRepository.find()` and `SQLiteBookRepository._lookup_work_id()` use it. |
| **list() → list_all() rename** | all repos, services, CLI handlers, tests | Renamed to eliminate method-name shadowing with builtin `list` type; dropped `typing.List` in favor of builtin `list[X]`, resolving 53 ruff violations. |
| **main() exception widening** | `interfaces/cli/main.py` | Now catches `TypeError` alongside `ValueError` for friendly error output. |
| **Travel find case-insensitivity** | `repositories/sql/sqlite_travel_repository.py` | `find()` now uses `LOWER()` on origin/destination, matching Address/Education repos. |
| **Work/Employment update WHERE** | `repositories/sql/sqlite_work_repository.py`, `sqlite_employment_repository.py` | `update()` WHERE clause narrowed to identity fields only (author/title/year for Work, company/start for Employment) — no longer includes non-identity fields that could cause stale-object `FolioNotFoundError`. |
| **ValueError catch** | `interfaces/cli/main.py` | Added `ValueError` to caught exceptions so bad user input (e.g. invalid dates) shows a friendly error instead of a traceback. |
| **Employment.__str__ safety** | `models/employment.py` | `__str__` now wraps `self.duration` in try/except to handle future-dated open-ended records. |
| **Work genre stripping** | `models/work.py` | `genre` field is now stripped in `__post_init__`, consistent with all other string fields across models. |
| **Book shared UoW** | `interfaces/cli/book.py` | `_remove` and `_replace` now share one `BookSQLiteUoW` between `WorkService` and `BookService` instead of creating two independent instances. |
