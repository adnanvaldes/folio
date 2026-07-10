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
- `_find_one(service, **kwargs)` — fetches exactly one record or raises ValueError (all domains including address)
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

## Tests (436 total, ~0.3s runtime)

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
4d46139 (HEAD -> main) test(book): add ISBN-less exact-duplicate integration test
5597fb6 refactor(repos): extract shared _work_identity_where helper
1772ff6 fix(cli): use find-then-mutate for address remove/replace
32e84f5 fix(timeline): narrow open-address overlap guard to ABSORB only
7ccd741 fix(models): strip whitespace in Work.__post_init__
e9c88f5 docs: add comprehensive AGENTS.md for project context
6f54432 chore: bump version to 1.0.1
5a47e42 refactor(services): use typing.List for consistency with repositories
cbdc0d4 refactor: use typing.List to avoid list() method name shadowing
bcfd2fd chore(deps): update uv.lock
```

No tags. Branch `main` after history rewrite.

---

## Next Steps / Roadmap

### Immediate
- **Release v1.0.1** — `git tag v1.0.1 && git push origin v1.0.1 && gh release create v1.0.1 --generate-notes`
- **Add release workflow** — `.github/workflows/release.yml` to auto-build and publish on tag push

### Features
- **Additional filter operators** — `find` is exact-match only; add `--before`, `--after`, `--contains` for real-world search
- **Import/export** — CSV and/or YAML import/export for bulk loading and migration
- **Stats command** — e.g., `folio travel stats` with "countries visited per year", most-traveled routes, etc.
- **Configurable ordering** — `--sort-by` flag or config option per domain

### Architecture
- **TUI with Textual** — second `interfaces/` adapter, reusing existing services/repos unchanged
- **Web interface** — FastAPI or similar as another adapter

### Polish
- **Remove `# type: ignore[attr-defined]`** — ~32 annotations in UoW layer from dynamic repo attributes; refactor with `__getattr__` or generic parameter
- **Specific exception types** — replace bare `ValueError` with domain-specific exceptions
- **Better test coverage** — add CLI handler tests, edge cases in timeline/ISBN validation

---

## Recent Fixes

| Fix | Files | Description |
|---|---|---|
| **Work field normalization** | `models/work.py` | `__post_init__` now strips author/title via `object.__setattr__`, matching Address/Employment/Travel. Prevents SQL lookup failures on whitespace-padded inputs. |
| **Address CLI find-then-mutate** | `interfaces/cli/address.py` | `_remove` and `_replace` now use `_find_one()` to fetch the DB-hydrated record first, preventing race conditions between domain equality (case-insensitive) and SQLite DELETE/UPDATE (exact-case). |
| **Open-address overlap guard** | `models/timeline.py` | Narrowed from broad `not existing.is_open or existing.start >= new.start` to `kind is _OverlapKind.ABSORB`. TRUNCATE_BACK now falls through to `needs_confirmation` as intended. |
| **Identity logic consolidation** | `repositories/sql/sqlite_work_repository.py` + `sqlite_book_repository.py` | Extracted `_work_identity_where()` helper; both `SQLiteWorkRepository.find()` and `SQLiteBookRepository._lookup_work_id()` use it. |
| **main() exception widening** | `interfaces/cli/main.py` | Now catches `TypeError` alongside `ValueError` for friendly error output.
