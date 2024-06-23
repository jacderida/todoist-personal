import questionary

from rich.console import Console

from todoist.helpers import date_picker
from todoist.tasks import get_full_label_names


ENTERTAINMENT_PROJECT_ID = 2319623017


def films_schedule(api):
    print("Pick a date")
    date = date_picker()
    film_title = questionary.text("Which film?").ask()

    console = Console()
    with console.status("[bold green]Creating task on Todoist...") as _:
        api.add_task(
            content=f"Watch *{film_title}*",
            labels=get_full_label_names(api, ["films", "entertainment", "home"]),
            project_id=ENTERTAINMENT_PROJECT_ID,
            due_date=date.strftime("%Y-%m-%d"))
