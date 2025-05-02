import typer

from db.db import engine, SQLModel, create_db_and_tables
from books import books

app = typer.Typer()
app.add_typer(books.app, name="books")

if __name__ == "__main__":
    create_db_and_tables()
    app()
