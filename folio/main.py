import typer

from db.db import engine, SQLModel, create_db_and_tables
from books import books

app = typer.Typer(no_args_is_help=True)
app.add_typer(books.app, name="books")


@app.command()
def init_db():
    """Initialize database file and create all required tables"""
    create_db_and_tables()


if __name__ == "__main__":
    app()
