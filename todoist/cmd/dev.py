import questionary
import toml

from pathlib import Path

from todoist.tasks import create_task, create_subtask, WorkType, TaskType


ARCHIVE_WIT_PROJECT_ID = 2324943655
ARCHIVE_WIT_PATH = "/home/chris/dev/github.com/jacderida/archive-witness-db-tools"
ENVIRONMENTS_PROJECT_ID = 2342779557
NODE_MANAGER_PROJECT_ID = 2321515089
AUTONOMI_PR_URL = "https://github.com/maidsafe/autonomi/pull/"
AUTONOMI_RC_RELEASE_URL = "https://github.com/maidsafe/autonomi/releases/tag/rc"
AUTONOMI_STABLE_RELEASE_URL = "https://github.com/maidsafe/autonomi/releases/tag/stable"

def dev_environments_comparison(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    first_environment_name = questionary.text("Name of the first environment?").ask()
    test_type = questionary.select(
        "TEST environment type",
        choices=["PR", "Branch", "RC"]
    ).ask()

    test_title = ""
    if test_type == "PR":
        pr_number = questionary.text("PR#?").ask()
        test_title = f"[[#{pr_number}]({AUTONOMI_PR_URL}/{pr_number})]"
    elif test_type == "Branch":
        branch_ref = questionary.text("Branch ref?").ask()
        test_title = f"[`{branch_ref}`]"
    elif test_type == "RC":
        rc_version = questionary.text("RC version?").ask()
        test_title = f"[[{rc_version}]({AUTONOMI_RC_RELEASE_URL}-{rc_version})]"

    second_environment_name = questionary.text("Name of the second environment?").ask()
    release_version = questionary.text("Release version?").ask()

    task = create_task(
        api,
        (
            f"`TEST`: `{first_environment_name}` "
            f"{test_title} vs "
            f"`REF`: `{second_environment_name}` "
            f"[[{release_version}]({AUTONOMI_STABLE_RELEASE_URL}-{release_version})]"
        ),
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)

    create_subtask(
        api,
        f"Define specification for `{first_environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        f"Define specification for `{second_environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)

    for env in [first_environment_name, second_environment_name]:
        create_subtask(
            api,
            f"Deploy `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
        create_subtask(
            api,
            f"Smoke test `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
        create_subtask(
            api,
            f"Provide additional funding for `{env}` (if applicable)",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    create_subtask(
        api,
        "Create comparison in the runner database",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Post comparison in Slack",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Process results",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Record results in runner database",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Drain funds from each environment",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    for env in [first_environment_name, second_environment_name]:
        create_subtask(
            api,
            f"Destroy `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)


def dev_environments_upscale_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    environment_name = questionary.text("Name of the environment?").ask()
    binary_option = questionary.select(
        "Binary option",
        choices=["PR", "Branch", "RC", "Stable"]
    ).ask()

    binary_option_text = ""
    if binary_option == "PR":
        pr_number = questionary.text("PR#?").ask()
        binary_option_text = f"[[#{pr_number}]({AUTONOMI_PR_URL}/{pr_number})]"
    elif binary_option == "Branch":
        branch_ref = questionary.text("Branch ref?").ask()
        binary_option_text = f"[`{branch_ref}`]"
    elif binary_option == "RC":
        rc_version = questionary.text("RC version?").ask()
        binary_option_text = f"[[{rc_version}]({AUTONOMI_RC_RELEASE_URL}-{rc_version})]"
    elif binary_option == "Stable":
        stable_version = questionary.text("Stable version?").ask()
        binary_option_text = f"[[{stable_version}]({AUTONOMI_STABLE_RELEASE_URL}-{stable_version})]"

    initial_node_count = questionary.text(
        "Initial node VM count?",
        validate=lambda text: text.isdigit()
    ).ask()
    initial_node_count = int(initial_node_count)

    increment_size = questionary.text(
        "Increment size?",
        validate=lambda text: text.isdigit()
    ).ask()
    increment_size = int(increment_size)

    increment_count = questionary.text(
        "How many increments?",
        validate=lambda text: text.isdigit()
    ).ask()
    increment_count = int(increment_count)

    task = create_task(
        api,
        f"Upscale Test Run: `{environment_name}` {binary_option_text}",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)
    create_subtask(
        api,
        f"Define inputs for launch network workflow",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)

    start = initial_node_count
    for _ in range(0, increment_count):
        end = start + increment_size
        create_subtask(
            api,
            f"Define specification for upscaling workflow for {start} to {end}",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
        start = end

    create_subtask(
        api,
        f"Deploy `{environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        f"Smoke test `{environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        f"Provide additional funding for `{environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)

    start = initial_node_count
    for _ in range(0, increment_count):
        end = start + increment_size
        create_subtask(
            api,
            f"Run upscaling workflow for {start} to {end}",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
        start = end

    create_subtask(
        api,
        f"Drain funds for `{environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        f"Destroy `{environment_name}`",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)


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
        "`sudo safenode-manager add --count 20 --node-port 12000-12019 --peer <peer-id>`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager status` [should be `ADDED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager start`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager status` [should be `RUNNING`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager stop`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager status` [should be `STOPPED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager remove`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager status` [should be empty]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager status --details` [all nodes should be `REMOVED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`sudo safenode-manager reset`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)


def dev_tests_nodeman_windows_smoke_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    task = create_task(
        api,
        "Node Manager and Launchpad smoke test on Windows",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)
    create_subtask(
        api,
        "`safenode-manager add --count 20 --node-port 12000-12019 --peer <peer-id>`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `ADDED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager start`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `RUNNING`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager stop`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `STOPPED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager start`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `RUNNING`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Restart the machine",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `STOPPED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager start`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `RUNNING`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager stop`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager status` [should be `STOPPED`]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager reset`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`node-launchpad --peer <peer-id>`",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Use `ctrl+g` to start 5 nodes (initial NAT detection takes a long time)",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Use `ctrl+x` to stop the nodes",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Use `ctrl+s` to start the nodes again",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Use q to quit the launchpad",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`node-launchpad --peer <peer-id>` [nodes should still be running]",
        NODE_MANAGER_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "`safenode-manager reset`",
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
