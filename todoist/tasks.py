import sys

from enum import auto, Enum

from rich.console import Console


class TaskType(Enum):
    ADMIN = auto()
    DEV = auto()
    INVESTIGATION = auto()
    RESEARCH = auto()


class WorkType(Enum):
    WORK = auto()
    PERSONAL = auto()


def create_subtask(
    api,
    content,
    project_id,
    task_type,
    work_type,
    parent_id,
    extra_labels=[],
    comment="",
):
    return create_task(
        api, content, project_id, task_type, work_type, parent_id, extra_labels, comment
    )


def create_task(
    api,
    content,
    project_id,
    task_type,
    work_type,
    parent_id=None,
    extra_labels=[],
    comment="",
    apply_date=False,
    section_id=None,
):
    console = Console()
    with console.status("[bold green]Creating task on Todoist...") as _:
        due = None
        if apply_date:
            due = None if parent_id else "Today"
        task = api.add_task(
            content=content,
            due_string=due,
            labels=get_full_label_names(
                api, get_labels_for_task(task_type, work_type, extra_labels)
            ),
            parent_id=parent_id,
            project_id=project_id,
            section_id=section_id
        )
        if parent_id:
            print("Created subtask '{name}'".format(name=task.content))
        else:
            print("Created task '{name}'".format(name=task.content))
    if comment:
        api.add_comment(task_id=task.id, content=comment)
        print("Added comment to '{name}'".format(name=task.content))
    return task


def get_full_label_names(api, label_names):
    retrieved_labels = api.get_labels()
    full_label_names = []
    for label in label_names:
        try:
            if label == "work":
                label_name = [x.name for x in retrieved_labels if label in x.name][1]
            else:
                label_name = next(x.name for x in retrieved_labels if label in x.name)
            full_label_names.append(label_name)
        except StopIteration:
            print("Label '{label}' doesn't exist. Please respecify with a valid label.".format(
                label=label))
            sys.exit(1)
    return full_label_names


def get_labels_for_task(task_type, work_type, extra_labels):
    labels = []
    if work_type == WorkType.WORK:
        labels.append("work")
    elif work_type == WorkType.PERSONAL:
        labels.append("home")

    if task_type == TaskType.ADMIN:
        labels.append("admin")
        labels.append("development")
    elif task_type == TaskType.INVESTIGATION:
        labels.append("investigation")
        labels.append("development")
    elif task_type == TaskType.RESEARCH:
        labels.append("research")
    elif task_type == TaskType.DEV:
        labels.append("development")

    return labels + extra_labels
