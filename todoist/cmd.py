import questionary

from .tasks import create_task, WorkType, TaskType


ARCHIVE_PROJECT_ID = 2288914343
TAPE_LOCATE_SECTION_ID = 156613680


def sept11_nist_assoc_dir_with_tape(api, tasks_path):
    work_type = WorkType.PERSONAL
    task_type = TaskType.RESEARCH

    if tasks_path:
        with open(tasks_path, "r") as f:
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
