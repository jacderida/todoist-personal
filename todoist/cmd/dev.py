import questionary
import toml

from pathlib import Path

from todoist.tasks import create_task, create_subtask, WorkType, TaskType


ARCHIVE_WIT_PROJECT_ID = 2324943655
ARCHIVE_WIT_PATH = "/home/chris/dev/github.com/jacderida/archive-witness-db-tools"
NODE_MANAGER_PROJECT_ID = 2321515089


def dev_releases_aw_release_checklist(api):
    work_type = WorkType.PERSONAL
    task_type = TaskType.DEV

    db_version = f'db-v{get_crate_version(Path(ARCHIVE_WIT_PATH) / "db" / "Cargo.toml")}'
    db_youtube_version = f'db-youtube-v{get_crate_version(Path(ARCHIVE_WIT_PATH) / "db-youtube" / "Cargo.toml")}'
    tools_version = f'tools-v{get_crate_version(Path(ARCHIVE_WIT_PATH) / "tools" / "Cargo.toml")}'

    print(f"Current version of db is {db_version}")
    print(f"Current version of db-youtube is {db_youtube_version}")
    print(f"Current version of tools is {tools_version}")

    print("Bump types: major, minor, patch or none")

    db_bump_type = questionary.text(
        f'Get db bump with `git log "{db_version}"..HEAD -- db`:',
    ).ask()
    db_youtube_bump_type = questionary.text(
        f'Get db-youtube bump with `git log "{db_youtube_version}"..HEAD -- db-youtube`:',
    ).ask()
    tools_bump_type = questionary.text(
        f'Get tools bump with `git log "{tools_version}"..HEAD -- tools`:',
    ).ask()

    task = create_task(
        api, "New release checklist", ARCHIVE_WIT_PROJECT_ID, task_type, work_type, apply_date=True)
    create_subtask(
        api,
        "Run `cargo clippy --all-targets --all-features -- -Dwarnings`",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Proof read commits and reword if necessary",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    if db_bump_type != "none":
        create_subtask(
            api,
            f"Bump db crate: `cargo release version --execute --package db {db_bump_type}`",
            ARCHIVE_WIT_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    if db_youtube_bump_type != "none":
        create_subtask(
            api,
            f"Bump db-youtube crate: `cargo release version --execute --package db-youtube {db_bump_type}`",
            ARCHIVE_WIT_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    if tools_bump_type != "none":
        create_subtask(
            api,
            f"Bump tools crate: `cargo release version --execute --package tools {tools_bump_type}`",
            ARCHIVE_WIT_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    create_subtask(
        api,
        "Get unreleased changelog: `git cliff --unreleased --tag <new version num>`",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Update the changelog with the new changes",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Put the new crate version numbers in the new changelog entry",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Create a `chore(release): tools-vX.Y.Z; db-vX.Y.Z; db-youtube-vX.Y.Z` commit",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Checkout `main` and rebase the feature branch in",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Generate tags: `cargo release tag --workspace --execute`",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Push tags: `cargo release push --execute`",
        ARCHIVE_WIT_PROJECT_ID,
        task_type,
        work_type,
        task.id)


def dev_tests_nodeman_linux_smoke_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    task = create_task(
        api,
        "Node Manager smoke test on Linux",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)
    create_subtask(
        api,
        "Add 20 nodes: `sudo safenode-manager add --count 20 --node-port 12000-12019 --peer <peer-id>`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Status should be `ADDED`: `sudo safenode-manager status`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Start nodes: `sudo safenode-manager start`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Status should be `RUNNING`: `sudo safenode-manager status`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Stop the nodes: `sudo safenode-manager stop`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Status should be `STOPPED`: `sudo safenode-manager status`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Remove the nodes: `sudo safenode-manager remove`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "No services should be shown: `sudo safenode-manager status",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Status should be `REMOVED` in detailed view: `sudo safenode-manager status --details`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Remove all traces: `sudo safenode-manager reset`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
#
# Helpers
#
def get_crate_version(toml_path):
    with open(toml_path, 'r') as file:
        cargo_toml = toml.load(file)
    return cargo_toml['package']['version']
