import typer

from db import engine, SQLModel
from books import books

app = typer.Typer()
app.add_typer(books.app, name="books")

if __name__ == "__main__":
    app()
