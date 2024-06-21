import questionary

from todoist.tasks import create_task, WorkType, TaskType


ARCHIVE_PROJECT_ID = 2288914343
TAPE_LOCATE_SECTION_ID = 156613680
UNCATEGORIZED_SECTION_ID = 158372860


def sept11_nist_add_uncategorized(api):
    work_type = WorkType.PERSONAL
    task_type = TaskType.RESEARCH
    name = questionary.text(
        "Provide the directory or file reference:",
        validate=lambda answer: True if len(answer) > 0 else "A value must be provided"
    ).ask()
    create_task(
        api,
        f"Add `{name}` as an uncategorized video",
        ARCHIVE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=False,
        section_id=UNCATEGORIZED_SECTION_ID)


def sept11_nist_assoc_dir_with_tape(api, dir_list_path):
    work_type = WorkType.PERSONAL
    task_type = TaskType.RESEARCH

    if dir_list_path:
        with open(dir_list_path, "r") as f:
            for line in f.readlines():
                name = line.strip()
                create_task(
                    api,
                    f"Attempt to locate the `{name}` in the NIST tapes database",
                    ARCHIVE_PROJECT_ID,
                    task_type,
                    work_type,
                    apply_date=False,
                    section_id=TAPE_LOCATE_SECTION_ID)
    else:
        name = questionary.text(
            "Provide the directory name:",
            validate=lambda answer: True if len(answer) > 0 else "A name for the tape must be provided"
        ).ask()
        create_task(
            api,
            f"Attempt to locate the `{name}` in the NIST tapes database",
            ARCHIVE_PROJECT_ID,
            task_type,
            work_type,
            apply_date=True,
            section_id=TAPE_LOCATE_SECTION_ID)


def sept11_nist_locate_tape(api, tapes_list_path):
    work_type = WorkType.PERSONAL
    task_type = TaskType.RESEARCH

    if tapes_list_path:
        with open(tapes_list_path, "r") as f:
            for line in f.readlines():
                name = line.strip()
                create_task(
                    api,
                    f"Attempt to locate the `{name}` tape in the 911datasets.org releases",
                    ARCHIVE_PROJECT_ID,
                    task_type,
                    work_type,
                    apply_date=False,
                    section_id=TAPE_LOCATE_SECTION_ID)
    else:
        name = questionary.text(
            "Provide the tape name:",
            validate=lambda answer: True if len(answer) > 0 else "A name for the tape must be provided"
        ).ask()
        create_task(
            api,
            f"Attempt to locate the `{name}` tape in the 911datasets.org releases",
            ARCHIVE_PROJECT_ID,
            task_type,
            work_type,
            apply_date=True,
            section_id=TAPE_LOCATE_SECTION_ID)
