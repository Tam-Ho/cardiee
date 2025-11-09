import random
from collections import deque
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .core import (
    DB_PATH,
    ERRORS,
    SUCCESS,
    __app_name__,
    __version__,
    cardiee,
    database,
)

app = typer.Typer()


def get_cardiee() -> cardiee.Cardiee:
    db_path = Path(DB_PATH) if not isinstance(DB_PATH, Path) else DB_PATH
    if db_path.exists():
        return cardiee.Cardiee()
    else:
        typer.secho(
            'Database not found. Please, run "cardiee init"', fg=typer.colors.RED
        )


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def version(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    pass


@app.command()
def init() -> None:
    """
    Initialize the database.
    """
    database_init_code = database._init_database(DB_PATH)
    if database_init_code != SUCCESS:
        typer.secho(
            f"Initializing database failed with {ERRORS[database_init_code]}.",
            fg=typer.colors.RED,
        )
    else:
        typer.secho("Initializing the database succeeded.", fg=typer.colors.GREEN)


@app.command()
def add(
    question: Annotated[str, typer.Argument(help="The question of the flashcard.")],
    answer: Annotated[str, typer.Argument(help="The answer of the flashcard.")],
) -> None:
    """
    Add a new flashcard with user input answer.
    """
    cardiee = get_cardiee()
    if cardiee:
        card, code = cardiee.add_card(question, answer)
        if code == SUCCESS:
            typer.secho(
                f"Flashcard added with ID: {card.id}, Question: {question}, Answer: {answer}, Deadline: {card.deadline}.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(f"Error adding flashcard: {ERRORS[code]}", fg=typer.colors.RED)


@app.command()
def remove(
    id: Annotated[int, typer.Argument(help="The ID of the flashcard to remove.")],
) -> None:
    """
    Remove a flashcard with card id.
    """
    cardiee = get_cardiee()

    typer.confirm(
        f"Are you sure you want to delete flashcard with ID: {id}?", abort=True
    )

    if cardiee:
        code = cardiee.remove_card(id)
        if code == SUCCESS:
            typer.secho(f"Flashcard with ID: {id} removed.", fg=typer.colors.GREEN)
        else:
            typer.secho(
                f"Error removing flashcard: {ERRORS[code]}", fg=typer.colors.RED
            )


@app.command()
def list() -> None:
    """
    List all flashcards.
    """
    cardiee = get_cardiee()
    if cardiee:
        cards, code = cardiee.list_cards(expired_only=False)
        if code == SUCCESS:
            if cards:
                console = Console()
                table = Table(
                    "ID", "Question", "Answer", "Deadline", header_style="bold cyan"
                )
                for card in cards:
                    table.add_row(
                        str(card.id), card.question, card.answer, str(card.deadline)
                    )
                console.print(table)
            else:
                typer.secho("No flashcards found.", fg=typer.colors.YELLOW)
        else:
            typer.secho(
                f"Error retrieving flashcards: {ERRORS[code]}", fg=typer.colors.RED
            )


@app.command()
def clear() -> None:
    """
    Clear all flashcards.
    """
    cardiee = get_cardiee()

    typer.confirm("Are you sure you want to delete all flashcards?", abort=True)

    if cardiee:
        code = cardiee.clear_cards()
        if code == SUCCESS:
            typer.secho("All flashcards cleared.", fg=typer.colors.GREEN)
        else:
            typer.secho(
                f"Error clearing flashcards: {ERRORS[code]}", fg=typer.colors.RED
            )


@app.command()
def study() -> None:
    """
    Start a study session for expired flashcards.
    """
    cardiee = get_cardiee()
    if cardiee:
        cards, code = cardiee.list_cards(expired_only=True)
        if code == SUCCESS:
            if cards:
                typer.secho(
                    f"There are {len(cards)} expired flashcards available for study."
                )
                typer.confirm(
                    "Do you want to start studying these flashcards?", abort=True
                )

                random.shuffle(cards)
                queue = deque(cards)
                total = len(cards)
                correct_count = 0
                seen = set()

                while queue:
                    card = queue.popleft()
                    typer.secho(
                        f"Question {correct_count + 1}/{total}: {card.question}"
                    )
                    user_input = typer.prompt(
                        "Your answer", default="", show_default=False
                    )
                    if user_input.strip().lower() == card.answer.strip().lower():
                        typer.secho("Correct!", fg=typer.colors.GREEN)
                        correct_count += 1
                        seen.add(card.id)
                    else:
                        typer.secho(
                            f"Incorrect. The correct answer is: {card.answer}",
                            fg=typer.colors.RED,
                        )
                        # Only re-add if not already seen this round
                        if card.id not in seen:
                            queue.append(card)
            else:
                typer.secho("No expired flashcards found.", fg=typer.colors.GREEN)
        else:
            typer.secho(
                f"Error retrieving flashcards: {ERRORS[code]}", fg=typer.colors.RED
            )


# @app.command()
# def ask(question: Annotated[str, typer.Argument()], skip: Annotated[bool, typer.Option("--skip", "-s", help="Skip logging the question")] = False) -> None:
#     cardiee = get_cardiee()
#     if not skip:
#         card, error = cardiee.add_card(question, "Answer example")
#         if error:
#             typer.secho(
#                 f'Adding card failed with {ERRORS[error]}.',
#                 fg=typer.colors.RED
#             )
#         typer.echo(f"Answer for your question: ...")
#         typer.echo(
#             f"Flashcard added to your deck with question: {question}, answer: ..."
#         )
#     else:
#         typer.echo(f"Answer for your question: ...")
