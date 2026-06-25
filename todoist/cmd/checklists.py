from rich.console import Console

from ..tasks import get_full_label_names

ROUTINE_PROJECT_ID = "6VF269FwQHvQ344P"
CI_RELEASE_PROJECT_ID = "6fpM8J7qG7qjxf9f"


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
                    "Review for leftover instances",
                    "Review infrastructure costs in #monitoring-infra-costings",
                    "Review production Grafana dashboard",
                    "Review Hermes report on `ant-prod-01` instances",
                    "Review Hermes report on production downloads",
                ],
            ),
            (
                "Capture work by reviewing the following",
                [
                    "Slack",
                    "Discord",
                    "Email",
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
            ("Use the `dev sync-todoist-from-linear` command to update Todoist", []),
            ("Select work from each project", []),
            ("Use the `dev sync-linear-from-todoist` command to update Linear", []),
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


def checklists_work_process_staging_results(api):
    console = Console()
    labels = get_full_label_names(api, ["checklist"])

    with console.status("[bold green]Creating process staging results tasks on Todoist..."):
        parent = api.add_task(
            content="Process staging results",
            project_id=CI_RELEASE_PROJECT_ID,
            labels=labels,
            due_string="today",
        )
        print(f"Created task '{parent.content}'")

        subtasks = [
            "Stop production downloader on `STG-03`",
            "Stop uploaders and downloaders on `STG-01` and `STG-02`",
            "Use the testnet comparator dashboard to view `STG-01` vs `STG-02`",
            "Generate comparison report for `STG-01` vs `STG-02`",
            "Generate upload/download summary report for `STG-01` vs `STG-02`",
            "Fetch upload logs from `STG-04`",
            "Generate production upload report for `STG-04`",
            "Obtain sign off from Qi on comparison report",
            "Obtain sign off from Nic for release",
        ]

        for subtask_content in subtasks:
            subtask = api.add_task(
                content=subtask_content,
                project_id=CI_RELEASE_PROJECT_ID,
                parent_id=parent.id,
            )
            print(f"Created subtask '{subtask.content}'")
