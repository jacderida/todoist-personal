from rich.console import Console

from ..tasks import get_full_label_names

ROUTINE_PROJECT_ID = "6VF269FwQHvQ344P"


def checklists_work_daily_planning(api):
    console = Console()
    labels = get_full_label_names(api, ["review"])

    with console.status("[bold green]Creating daily planning tasks on Todoist..."):
        parent = api.add_task(
            content="Daily Planning",
            project_id=ROUTINE_PROJECT_ID,
            labels=labels,
            due_string="today",
        )
        print(f"Created task '{parent.content}'")

        subtasks = [
            (
                "Infrastructure check up",
                [
                    "Review droplet list for leftover droplets",
                    "Check Digital Ocean estimated billing value",
                    "Review `Default V6` dashboard",
                    "Review `Mainnet Continuous Downloader` dashboard",
                ],
            ),
            (
                "Capture work by reviewing the following",
                [
                    "Slack",
                    "Discord",
                    "Email",
                    "Forum",
                ],
            ),
            (
                "Process each captured inbox item",
                [
                    "Add item to Linear if applicable",
                    "Update any existing Linear issue with comments if applicable",
                    "Add item to Todoist if not captured in Linear",
                ],
            ),
            ("Use the `dev linear-sync` command to update Todoist", []),
            ("Select work from each project", []),
            ("Review waiting/delegated/blocked tasks", []),
            ("Organise and prioritise the work on the Kanban board", []),
        ]

        for subtask_content, children in subtasks:
            subtask = api.add_task(
                content=subtask_content,
                project_id=ROUTINE_PROJECT_ID,
                parent_id=parent.id,
            )
            print(f"Created subtask '{subtask.content}'")

            for child_content in children:
                child = api.add_task(
                    content=child_content,
                    project_id=ROUTINE_PROJECT_ID,
                    parent_id=subtask.id,
                )
                print(f"Created subtask '{child.content}'")
