# folio

**folio** is a work-in-progress command-line application for managing personal collections built with Python and Typer. At the moment it provides a flexible way to catalog, search, and update books and literary works using a SQLite database. 


This project is 1) still being developed, and 2) designed to fulfill a personal need. I cannot guarantee that the API will remain stable.

It is created to serve a personal need - that is, to have a centralized interface for managing my books, my trips, and other data. Not all features have been implemented yet.

## Features

- **Add Works and/or Books**: Add a new literary work or book edition to your collection. If a work does not exist, it can be created on-the-fly.
- **Search/Update**: Flexible filtering for works and books by title, author, year, genre, read status, page count, format (print, ebook, audiobook, etc.), and ISBN.
- **Extensible**: Structured for easy extension and testing.

## Project Structure

```
folio/
├── __init__.py
├── books                   # Main books commands and logic
│  ├── args.py              # CLI argument definitions
│  ├── books.py             # Book-related commands
│  ├── models.py            # SQLModel definitions
│  └── schemas.py           # Dataclasses and enums
├── db
│  ├── db.py                # Database session and connections
│  └── query_builder.py     # SQL query constructor
├── main.py                 # CLI entry point
└── utils.py
```

## Command Overview

The CLI is implemented using [Typer](https://typer.tiangolo.com/):

- `add`: Add a new work or book to the database.
- `search`: Flexible search with multiple filters.
- `update`: Update attributes for works or books using search filters.
- `delete`: Delete specific entries from the database.

## Example Usage

```bash
# Initialize the database
uv run ./folio/main.py init-db

# Add a new work and book
uv run ./folio/main.py books add --title "1984" --author "George Orwell" --year 1949 --genre "Dystopian"

# Add a new edition (book) to an existing work
uv run ./folio/main.py books add_book --title "1984" --author "George Orwell" --pages 328 --format "print" --isbn 9780451524935

# Search for books by author and genre
uv run ./folio/main.py books search --author "Tolkien" --genre "fantasy"

# Update a book's read status
uv run ./folio/main.py books update --title "1984" --set_is_read true
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/adnanvaldes/folio.git
   cd folio
   ```

2. [Install uv](https://github.com/astral-sh/uv) if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Create a virtual environment and run `uv`:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

4. Initialize the database:
   ```bash
   uv run ./folio/main.py init_db
   ```

## Development and Testing

- Tests are in `folio/tests/` and use `pytest`.
- To run all tests:
  ```bash
  uv pip install pytest
  pytest
  ```


## Development and Testing

- Tests are in `folio/tests/` and use `pytest`.
- To run all tests:
  ```bash
  pytest folio/tests/
  ```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**folio** is intended as a personal command-line cataloging tool, but its structure allows for easy adaptation to other collection management needs. Contributions and issues are welcome!