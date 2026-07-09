# Changelog

## 1.0.0

First stable release.

### Added
- Five domains: travel, address, work, book, employment
- Full CLI with `add`, `list`, `find`, `remove`, `replace` (and `update` for work/employment)
- Timeline management for addresses with automatic conflict detection
- ISBN validation for books
- JSON output via `--json` flag
- Custom database and config paths via `--db` and `--config` flags
- 433 tests (unit and integration)

### Architecture
- Clean Architecture with Repository ABCs and SQLite implementations
- Unit of Work pattern for transaction management
- Frozen dataclass models with identity-based equality
- XDG-compliant config and data paths
