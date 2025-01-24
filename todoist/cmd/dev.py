import os
import questionary
import shutil
import toml

from pathlib import Path

from todoist.tasks import create_task, create_subtask, WorkType, TaskType


ARCHIVE_WIT_PROJECT_ID = 2324943655
ARCHIVE_WIT_PATH = "/home/chris/dev/github.com/jacderida/archive-witness-db-tools"
AUTONOMI_PR_URL = "https://github.com/maidsafe/autonomi/pull/"
AUTONOMI_RC_RELEASE_URL = "https://github.com/maidsafe/autonomi/releases/tag/rc"
AUTONOMI_STABLE_RELEASE_URL = "https://github.com/maidsafe/autonomi/releases/tag/stable"
CI_RELEASE_PROJECT_ID = 2281501332
CURRENT_RELEASE_CYCLE_SECTION_ID = 167691411
DEPLOYMENTS_PROJECT_ID = 2347280389
DEPLOYMENT_INPUTS_PATH = Path("/home/chris/dev/github.com/jacderida/ant-network-workflow-runner/inputs")
ENVIRONMENTS_PROJECT_ID = 2342779557
NODE_MANAGER_PROJECT_ID = 2321515089
PROD_ENV_NAME = "PROD-01"


def dev_deployments_generate_markdown_post():
    package_version = questionary.text("Package version:").ask()
    antnode_version = questionary.text("antnode version:").ask()
    ant_version = questionary.text("ant version:").ask()
    antctl_version = questionary.text("antctl version:").ask()
    upgrade_antctl = questionary.confirm("Will antctl be upgraded?").ask()
    upgrade_antnode = questionary.confirm("Will antnode be upgraded?").ask()
    upgrade_ant = questionary.confirm("Will ant be upgraded?").ask()

    post_content = (
        f"Deployment checklist/guide for [{package_version}]({AUTONOMI_STABLE_RELEASE_URL}-{package_version}).\n\n"
        "The [workflow runner tool](https://github.com/maidsafe/ant-network-workflow-runner/) will be used to run all the upgrades.\n\n"
    )

    if upgrade_antctl:
        post_content += (
            "## Upgrade antctl\n\n"
            f"Upgrade `antctl` to `{antctl_version}` on `{PROD_ENV_NAME}`.\n\n"
            "[ ] Run `upgrade-antctl` against all hosts\n"
            "\n---\n\n"
        )
    if upgrade_antnode:
        post_content += (
            "## Upgrade antnode\n\n"
            f"Upgrade `antnode` to `{antnode_version}` on `{PROD_ENV_NAME}`.\n\n"
            f"This will be an *upgrade* rather than a *reset*, meaning the nodes will restart with the same peer ID and data.\n\n"
        )

        post_content += (
            "### Manually upgrade a single node\n\n"
            "[ ] Use `PROD-01-genesis-bootstrap` to manually upgrade one node\n"
            "[ ] Verify the node starts and remains running\n\n"
        )

        post_content += (
            "### Upgrade the fleet\n\n"
            f"These items can run in parallel if desired.\n\n"
            f"The process will run against one host at a time and there will be a 5-minute interval between processing each node.\n\n"
        )

        post_content += f"[ ] Run `upgrade-network` against peer cache hosts\n"
        post_content += f"[ ] Run `upgrade-network` against private hosts\n"

        current_host = 1
        end_host = 39
        increment_size = 9

        while current_host < end_host:
            start = current_host
            end = start + increment_size
            if end > end_host:
                end = end_host
            post_content += f"[ ] Run `upgrade-network` against generic hosts {start}-{end}\n"
            current_host = end + 1

        post_content += "\n---\n\n"
    if upgrade_ant:
        post_content += (
            "## Upgrade ant\n\n"
            f"Upgrade `ant` to `{ant_version}` on `{PROD_ENV_NAME}`.\n\n"
            "[ ] Run `upgrade-uploaders` to upgrade all uploader hosts\n"
            "\n---\n\n"
        )

    print(post_content.strip("\n---\n\n"))


def dev_deployments_upgrade(api):
    work_type = WorkType.PERSONAL
    task_type = TaskType.DEV

    package_version = questionary.text("Package version?").ask()
    stripped_version = ".".join(package_version.split(".")[:-1])
    ant_version = questionary.text("`ant` version?").ask()
    antnode_version = questionary.text("`antnode` version?").ask()
    antctl_version = questionary.text("`antctl` version?").ask()

    base_inputs_path = DEPLOYMENT_INPUTS_PATH / f"{stripped_version}" / "prod" / f"{package_version}"
    if os.path.exists(base_inputs_path):
        shutil.rmtree(base_inputs_path)
    base_inputs_path.mkdir(parents=True, exist_ok=True)

    file_number = 1
    upgrade_antctl_path = base_inputs_path / f"{file_number:02}-{PROD_ENV_NAME}-upgrade_antctl.yml"
    upgrade_antctl_content = (
        f"network-name: {PROD_ENV_NAME}\n"
        f"version: {antctl_version}"
    )
    with open(upgrade_antctl_path, "w") as file:
        file.write(upgrade_antctl_content)
    create_task(
        api,
        f"`{package_version}`: upgrade `antctl` to `{antctl_version}` [all hosts]",
        DEPLOYMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)

    create_task(
        api,
        f"`{package_version}`: manually upgrade one `antnode` to `{antnode_version}` on genesis host",
        DEPLOYMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)

    file_number += 1
    peer_cache_path = base_inputs_path / f"{file_number:02}-{PROD_ENV_NAME}-upgrade_network-peer_cache_hosts.yml"
    peer_cache_content = (
        f"network-name: {PROD_ENV_NAME}\n"
        f"version: {antnode_version}\n"
        f"ansible-forks: 1\n"
        f"interval: 300000\n"
        f"node-type: peer-cache"
    )
    with open(peer_cache_path, "w") as file:
        file.write(peer_cache_content)
    create_task(
        api,
        f"`{package_version}`: upgrade `antnode` to `{antnode_version}` [peer cache hosts]",
        DEPLOYMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)

    file_number += 1
    private_path = base_inputs_path / f"{file_number:02}-{PROD_ENV_NAME}-upgrade_network-private_hosts.yml"
    private_content = (
        f"network-name: {PROD_ENV_NAME}\n"
        f"version: {antnode_version}\n"
        f"ansible-forks: 1\n"
        f"interval: 300000\n"
        f"node-type: private"
    )
    with open(private_path, "w") as file:
        file.write(private_content)
    create_task(
        api,
        f"`{package_version}`: upgrade `antnode` to `{antnode_version}` [private hosts]",
        DEPLOYMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)

    file_number += 1
    current_host = 1
    end_host = 39
    increment_size = 9

    initial_generic_content = (
        f"network-name: {PROD_ENV_NAME}\n"
        f"version: {antnode_version}\n"
        f"ansible-forks: 1\n"
        f"interval: 300000\n"
        f"custom-inventory:\n"
    )
    while current_host < end_host:
        current = current_host
        end = current + increment_size
        generic_content = initial_generic_content
        if end > end_host:
            end = end_host

        create_task(
            api,
            f"`{package_version}`: upgrade `antnode` to `{antnode_version}` [generic hosts {current}-{end}]",
            DEPLOYMENTS_PROJECT_ID,
            task_type,
            work_type,
            apply_date=True)

        while current <= end:
            generic_content += f"  - {PROD_ENV_NAME}-node-{current}\n"
            current += 1
        generic_path = \
            base_inputs_path / f"{file_number:02}-{PROD_ENV_NAME}-upgrade_network-generic_hosts.yml"
        with open(generic_path, "w") as file:
            file.write(generic_content)
        current_host = current
        file_number += 1

    file_number += 1
    upgrade_uploaders_path = base_inputs_path / f"{file_number:02}-{PROD_ENV_NAME}-upgrade_uploaders.yml"
    uploaders_content = (
        f"network-name: {PROD_ENV_NAME}\n"
        f"version: {ant_version}\n"
    )
    with open(upgrade_uploaders_path, "w") as file:
        file.write(uploaders_content)
    create_task(
        api,
        f"`{package_version}`: upgrade `ant` to `{ant_version}` [uploaders]",
        DEPLOYMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True)


def dev_environments_comparison(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    purpose = questionary.text("Purpose of the test?").ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia"]
    ).ask()
    env_type = questionary.select(
        "What type/size of environments are required?",
        choices=["Development", "Staging"]
    ).ask()

    test_count = questionary.text(
        "Number of test environments?",
        validate=lambda text: text.isdigit()
    ).ask()
    test_count = int(test_count)

    environments = []
    task_title = "Environment Comparison -- "
    for i in range(0, test_count):
        print(f"TEST{i + 1} environment")
        name = questionary.text(f"Name?").ask()
        environments.append(name)

        test_type = questionary.select(
            "Type",
            choices=["PR", "Branch", "RC"]
        ).ask()
        task_title += f"`TEST{i + 1}`: `{name}` "
        if test_type == "PR":
            pr_number = questionary.text(
                "PR#?",
                validate=lambda text: text.isdigit()
            ).ask()
            pr_number = int(pr_number)
            task_title += f"[[#{pr_number}]({AUTONOMI_PR_URL}/{pr_number})]"
        elif test_type == "Branch":
            branch_ref = questionary.text("Branch ref?").ask()
            task_title += f"[`{branch_ref}`]"
        elif test_type == "RC":
            rc_version = questionary.text("RC version?").ask()
            task_title += f"[[{rc_version} RC]({AUTONOMI_RC_RELEASE_URL}-{rc_version})]"
        task_title += " vs "

    ref_env_name = questionary.text("Name of the REF environment?").ask()
    environments.append(ref_env_name)
    release_version = questionary.text("Release version?").ask()
    task_title += f" `REF`: `{ref_env_name}` "
    task_title += f"[[{release_version}]({AUTONOMI_STABLE_RELEASE_URL}-{release_version})]"
    task_title += f" [{env_type} Config]"
    task = create_task(
        api,
        task_title,
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        description=purpose,
        apply_date=True)

    for env in environments:
        create_subtask(
            api,
            f"Define specification for `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    for env in environments:
        for title in [
            f"Deploy `{env}`",
            f"Smoke test `{env}`",
        ]:
            create_subtask(
                api,
                title,
                ENVIRONMENTS_PROJECT_ID,
                task_type,
                work_type,
                task.id)
    if evm_type == "Sepolia":
        for env in environments:
            create_subtask(
                api,
                f"Provide additional funding for `{env}`",
                ENVIRONMENTS_PROJECT_ID,
                task_type,
                work_type,
                task.id)

    for title in [
        "Create comparison in the runner database",
        "Post comparison in Slack",
        "Process results for generic nodes",
        "Process results for private nodes",
        "Post results in Slack thread",
        "Record results in runner database",
    ]:
        create_subtask(
            api,
            title,
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    if evm_type == "Sepolia":
        for env in environments:
            create_subtask(
                api,
                f"Drain funds from {env}",
                ENVIRONMENTS_PROJECT_ID,
                task_type,
                work_type,
                task.id)
    for env in environments:
        create_subtask(
            api,
            f"Destroy `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)

def dev_environments_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    env_name = questionary.text("Name of the environment?").ask()
    purpose = questionary.text("Purpose of the test?").ask()
    binary_option = questionary.select(
        "Binary option",
        choices=["PR", "Branch", "RC", "Stable"]
    ).ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia"]
    ).ask()
    extra_funding = False
    if evm_type == "Sepolia":
        extra_funding = questionary.confirm("Is extra funding required?").ask()
    env_type = questionary.select(
        "What type/size of environments are required?",
        choices=["Development", "Staging"]
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

    task = create_task(
        api,
        f"Environment test: `{env_name}` {binary_option_text} [{env_type} Config]",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        description=purpose)
    for task_title in [
        "Define inputs for launch network workflow",
        f"Deploy environment",
        f"Smoke test environment",
    ]:
        create_subtask(
            api,
            task_title,
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    if evm_type == "Sepolia" and extra_funding:
        create_subtask(
            api,
            "Provide extra funding",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    create_subtask(
        api,
        "Gather results",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    if evm_type == "Sepolia":
        create_subtask(
            api,
            "Drain remaining funds",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    create_subtask(
        api,
        "Destroy environment",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)


def dev_environments_upscale_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    env_name = questionary.text("Name of the environment?").ask()
    purpose = questionary.text("Purpose of the test?").ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia"]
    ).ask()
    extra_funding = False
    if evm_type == "Sepolia":
        extra_funding = questionary.confirm("Is extra funding required?").ask()
    env_type = questionary.select(
        "What type/size of environments are required?",
        choices=["Custom", "Development", "Staging"]
    ).ask()

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

    task = create_task(
        api,
        f"Upscaling Test -- `{env_name}` {binary_option_text} [{env_type} Config]",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        description=purpose)
    for task_title in [
        "Define inputs for launch network workflow",
        "Define inputs for upscaling workflows",
        "Define scripts for running upscale workflows",
        "Deploy environment",
        "Smoke test environment",
    ]:
        create_subtask(
            api,
            task_title,
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    if evm_type == "Sepolia" and extra_funding:
        create_subtask(
            api,
            "Provide extra funding",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    create_subtask(
        api,
        "Gather results",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    if evm_type == "Sepolia":
        create_subtask(
            api,
            "Drain remaining funds",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)
    create_subtask(
        api,
        "Destroy environment",
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


def dev_releases_hotfix_existing_branches(api):
    work_type = WorkType.PERSONAL
    task_type = TaskType.DEV

    version = questionary.text("New package version?").ask()
    branch_num = questionary.text("Hotfix branch number?").ask()
    stripped_version = ".".join(version.split(".")[:-1])
    branch_name = f"rc-{stripped_version}-hotfix{branch_num}"

    stable_release_tasks = [
        f"Create a `{branch_name}` branch",
        f"Merge relevant PRs to the `{branch_name}` branch",
        f"On `{branch_name}`: increment `release-cycle-counter` in the `release-cycle-info` file",
        f"On `{branch_name}`: increment `RELEASE_CYCLE_COUNTER` in the `release_info.rs` file",
        f"On `{branch_name}`: provide changelog entries",
        f"On `{branch_name}`: bump crate versions with `cargo release version --package <crate-name> patch --execute`",
        f"On `{branch_name}`: create a `chore(release): stable {version}` commit",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `main`",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `stable`",
        "Push to `main` and `stable`",
        "Publish `sn_logging` manually",
        "Tag `sn_logging` manually",
        "Push tag to origin",
        "Prepare the release description",
        "Run the `release` workflow on the `stable` branch with a 4MB chunk size",
        "Update the Github release description",
        "On `stable`: publish crates with `release-plz`",
    ]
    task = create_task(
        api,
        f"`{version}` hotfix: stable release",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    for subtask in stable_release_tasks:
        create_subtask(
            api,
            subtask,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    task = create_task(
        api,
        f"`{version}` hotfix: post stable release thread on Discourse",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    create_subtask(
        api,
        "Post reply with release notes",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    create_subtask(
        api,
        "Define deployment plan",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        task.id)
    task = create_task(
        api,
        f"`{version}` hotfix: request community announcement",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)


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
