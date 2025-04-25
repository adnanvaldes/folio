import typer
from typing_extensions import Annotated

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from db import engine, SQLModel
from books import books

app = typer.Typer()
app.add_typer(books.app, name="books")

if __name__ == "__main__":
    app()
