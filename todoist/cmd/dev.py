import json
import os
import questionary
import re
import requests
import shutil
import toml
import uuid

from datetime import date
from linear_api import LinearClient
from linear_api.domain import LinearIssueUpdateInput
from pathlib import Path
from rich.console import Console

from todoist import cache
from todoist.tasks import create_task, create_subtask, get_full_label_names, WorkType, TaskType

console = Console()


ACTIVE_WORK_PROJECTS_SECTION_ID = 182988422
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
    environment = questionary.select(
        "Which environment?",
        choices=["alpha", "mainnet"]
    ).ask()
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
        if environment == "mainnet":
            end_host = 39
        elif environment == "alpha":
            end_host = 100
        else:
            raise ValueError()
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

    environment = questionary.select(
        "Which environment?",
        choices=["alpha", "mainnet"]
    ).ask()
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
    if environment == "mainnet":
        end_host = 39
    elif environment == "alpha":
        end_host = 100
    else:
        raise ValueError()
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


def dev_environments_bootstrap(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    new_env_name = questionary.text("Environment name?").ask()
    source_env_name = questionary.text("Source environment name?").ask()
    purpose = questionary.text("Purpose of the bootstrap?").ask()
    env_type = questionary.select(
        "What type/size of environment is required?",
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
        f"Bootstrap environment: `{new_env_name}` {binary_option_text} [{env_type} Config]",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        description=f"Bootstrapped from `{source_env_name}`. {purpose}")
    
    for task_title in [
        "Define inputs for bootstrap network workflow",
        "Bootstrap environment",
        "Smoke test environment",
    ]:
        create_subtask(
            api,
            task_title,
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


def dev_environments_bootstrap_comparison(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    purpose = questionary.text("Purpose of the test?").ask()
    env_type = questionary.select(
        "What type/size of environments are required?",
        choices=["Custom", "Development", "Staging"]
    ).ask()

    if env_type == "Custom":
        generic_hosts_count = questionary.text(
            "Number of generic node hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        generic_hosts_count = int(generic_hosts_count)
        generic_nodes_per_host_count = questionary.text(
            "Number of nodes on generic hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        generic_nodes_per_host_count = int(generic_nodes_per_host_count)

        symmetric_nat_hosts_count = questionary.text(
            "Number of symmetric NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        symmetric_nat_hosts_count = int(symmetric_nat_hosts_count)
        symmetric_nat_nodes_per_host_count = questionary.text(
            "Number of nodes on symmetric NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        symmetric_nat_nodes_per_host_count = int(symmetric_nat_nodes_per_host_count)

        full_cone_nat_hosts_count = questionary.text(
            "Number of full cone NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        full_cone_nat_hosts_count = int(full_cone_nat_hosts_count)
        full_cone_nat_nodes_per_host_count = questionary.text(
            "Number of nodes on full cone NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        full_cone_nat_nodes_per_host_count = int(full_cone_nat_nodes_per_host_count)

    test_count = questionary.text(
        "Number of test environments?",
        validate=lambda text: text.isdigit()
    ).ask()
    test_count = int(test_count)

    environments = []
    task_title = "Bootstrap Comparison -- "
    for i in range(0, test_count):
        print(f"TEST{i + 1} environment")
        name = questionary.text(f"Name?").ask()
        environments.append(name)

        test_type = questionary.select(
            "Type",
            choices=["PR", "Branch", "RC", "Release"]
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
        elif test_type == "Release":
            release_version = questionary.text("Version?").ask()
            task_title += f"[[{release_version}]({AUTONOMI_RC_RELEASE_URL}-{release_version})]"
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
            f"Bootstrap `{env}`",
            f"Smoke test `{env}`",
        ]:
            create_subtask(
                api,
                title,
                ENVIRONMENTS_PROJECT_ID,
                task_type,
                work_type,
                task.id)

    for title in [
        "Create comparison in the runner database",
        "Create issue in Linear",
        "Post comparison in Slack",
        "Produce comparison report",
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
    for env in environments:
        create_subtask(
            api,
            f"Destroy `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    if env_type == "Custom":
        print(f"generic-node-count: {generic_nodes_per_host_count}")
        print(f"full-cone-private-node-count: {full_cone_nat_nodes_per_host_count}")
        print(f"symmetric-private-node-count: {symmetric_nat_nodes_per_host_count}")

        print(f"generic-vm-count: {generic_hosts_count}")
        print(f"full-cone-private-vm-count: {full_cone_nat_hosts_count}")
        print(f"symmetric-private-vm-count: {symmetric_nat_nodes_per_host_count}")


def dev_environments_prod_bootstrap_comparison(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    purpose = questionary.text("Purpose of the test?").ask()
    env_type = questionary.select(
        "What type/size of environments are required?",
        choices=["Custom", "Development", "Staging"]
    ).ask()

    if env_type == "Custom":
        generic_hosts_count = questionary.text(
            "Number of generic node hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        generic_hosts_count = int(generic_hosts_count)
        generic_nodes_per_host_count = questionary.text(
            "Number of nodes on generic hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        generic_nodes_per_host_count = int(generic_nodes_per_host_count)

        symmetric_nat_hosts_count = questionary.text(
            "Number of symmetric NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        symmetric_nat_hosts_count = int(symmetric_nat_hosts_count)
        symmetric_nat_nodes_per_host_count = questionary.text(
            "Number of nodes on symmetric NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        symmetric_nat_nodes_per_host_count = int(symmetric_nat_nodes_per_host_count)

        full_cone_nat_hosts_count = questionary.text(
            "Number of full cone NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        full_cone_nat_hosts_count = int(full_cone_nat_hosts_count)
        full_cone_nat_nodes_per_host_count = questionary.text(
            "Number of nodes on full cone NAT hosts?",
            validate=lambda text: text.isdigit(),
            default="0"
        ).ask()
        full_cone_nat_nodes_per_host_count = int(full_cone_nat_nodes_per_host_count)

    test_count = questionary.text(
        "Number of test environments?",
        validate=lambda text: text.isdigit()
    ).ask()
    test_count = int(test_count)

    environments = []
    task_title = "Prod Bootstrap Comparison -- "
    for i in range(0, test_count):
        print(f"TEST{i + 1} environment")
        name = questionary.text(f"Name?").ask()
        environments.append(name)

        test_type = questionary.select(
            "Type",
            choices=["PR", "Branch", "RC", "Release"]
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
        elif test_type == "Release":
            release_version = questionary.text("Version?").ask()
            task_title += f"[[{release_version}]({AUTONOMI_RC_RELEASE_URL}-{release_version})]"
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

    for title in [
        "Create comparison in the runner database",
        "Create issue in Linear",
        "Post comparison in Slack",
        "Use testnet comparator dash to compare the environments",
        "Produce comparison report",
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
    for env in environments:
        create_subtask(
            api,
            f"Destroy `{env}`",
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    if env_type == "Custom":
        print(f"generic-node-count: {generic_nodes_per_host_count}")
        print(f"full-cone-private-node-count: {full_cone_nat_nodes_per_host_count}")
        print(f"symmetric-private-node-count: {symmetric_nat_nodes_per_host_count}")

        print(f"generic-vm-count: {generic_hosts_count}")
        print(f"full-cone-private-vm-count: {full_cone_nat_hosts_count}")
        print(f"symmetric-private-vm-count: {symmetric_nat_nodes_per_host_count}")


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
        choices=["Custom", "Development", "Staging"]
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
            choices=["PR", "Branch", "RC", "Release"]
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
        elif test_type == "Release":
            release_version = questionary.text("Version?").ask()
            task_title += f"[[{release_version}]({AUTONOMI_RC_RELEASE_URL}-{release_version})]"
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

    for title in [
        "Restart clients",
        "Create comparison in the runner database",
        "Create issue in Linear",
        "Post comparison in Slack",
        "Use testnet comparator dash to evaluate the environments",
        "Use the uploader dash to evaluate uploads for the environments",
        "Use the network dashboard script to generate the comparison HTML report",
        "Record the comparison results in the database using the comparison checklist",
        "Record the upload results",
        "Record the download results",
        "Post the report in the Slack thread",
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
                f"Drain funds from `{env}`",
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


def dev_environments_comparison_results_checklist(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    task_title = "Comparison Results Checklist"
    task = create_task(
        api,
        task_title,
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        extra_labels=["checklist"],
        apply_date=True)

    for title in [
        "Record log volume for TEST vs REF",
        "Generic nodes: summary of connected peers and open connections",
        "Generic nodes: summary of standard metrics",
        "Generic nodes: summary of libp2p metrics",
        "Generic nodes: use testnet comparator to verify ELK connection errors are similar",
        "Generic nodes: use testnet comparator to verify ELK connection actions are similar",
        "Generic nodes: verify earnings are non-zero with `Avg. Current ANT Wallet Balance Per Node By Host` metric",
        "Generic nodes: verify PUT record error rate is low or zero",
        "Static full cone nodes: summary of connected peers and open connections",
        "Static full cone nodes: summary of standard metrics",
        "Static full cone nodes: summary of libp2p metrics",
        "Static full cone nodes: use testnet comparator to verify ELK connection errors are similar",
        "Static full cone nodes: use testnet comparator to verify ELK connection actions are similar",
        "Static full cone nodes: verify earnings are non-zero with `Avg. Current ANT Wallet Balance Per Node By Host` metric",
        "Static full cone nodes: verify PUT record error rate is low or zero",
    ]:
        create_subtask(
            api,
            title,
            ENVIRONMENTS_PROJECT_ID,
            task_type,
            work_type,
            task.id)


def dev_environments_client_performance_comparison(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    purpose = questionary.text("Purpose of the test?").ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia", "ArbitrumOne"]
    ).ask()
    test_type = questionary.select(
        "Is it a download or upload test?",
        choices=["Download", "Upload", "Download/Upload"]
    ).ask()

    test_count = questionary.text(
        "Number of test environments?",
        validate=lambda text: text.isdigit()
    ).ask()
    test_count = int(test_count)

    environments = []
    task_title = "Client Performance Comparison -- "
    for i in range(0, test_count):
        print(f"TEST{i + 1} environment")
        name = questionary.text(f"Name?").ask()
        environments.append(name)

        test_bin_type = questionary.select(
            "Type",
            choices=["PR", "Branch", "RC", "Release"]
        ).ask()
        task_title += f"`TEST{i + 1}`: `{name}` "
        if test_bin_type == "PR":
            pr_number = questionary.text(
                "PR#?",
                validate=lambda text: text.isdigit()
            ).ask()
            pr_number = int(pr_number)
            task_title += f"[[#{pr_number}]({AUTONOMI_PR_URL}/{pr_number})]"
        elif test_bin_type == "Branch":
            branch_ref = questionary.text("Branch ref?").ask()
            task_title += f"[`{branch_ref}`]"
        elif test_bin_type == "RC":
            rc_version = questionary.text("RC version?").ask()
            task_title += f"[[{rc_version} RC]({AUTONOMI_RC_RELEASE_URL}-{rc_version})]"
        elif test_bin_type == "Release":
            release_version = questionary.text("Version?").ask()
            task_title += f"[[{release_version}]({AUTONOMI_RC_RELEASE_URL}-{release_version})]"
        task_title += " vs "

    ref_env_name = questionary.text("Name of the REF environment?").ask()
    environments.append(ref_env_name)
    release_version = questionary.text("Release version?").ask()
    task_title += f" `REF`: `{ref_env_name}` "
    task_title += f"[[{release_version}]({AUTONOMI_STABLE_RELEASE_URL}-{release_version})]"
    task_title += f" [{test_type}]"
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
        "Restart clients",
        "Create comparison in the runner database",
        "Post comparison in Slack",
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
                f"Drain funds from `{env}`",
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


def dev_environments_client_performance_test(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV
    
    env_name = questionary.text("Name of the environment?").ask()
    purpose = questionary.text("Purpose of the test?").ask()
    test_type = questionary.select(
        "Type of test?",
        choices=["Download", "Upload", "Download/Upload"]
    ).ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia", "Arbitrum One"]
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
        f"Client performance test: `{env_name}` {binary_option_text} [{test_type}]",
        ENVIRONMENTS_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        description=purpose)
    for task_title in [
        "Define inputs for client deploy workflow",
        "Deploy environment",
        "Smoke test environment",
        "Perform the test",
        "Report results",
        "Destroy the environment",
    ]:
        create_subtask(
            api,
            task_title,
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

def dev_environments_maintenance(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    env_name = questionary.text("Name of the environment?").ask()
    purpose = questionary.text("Maintenance purpose?").ask()
    binary_option = questionary.select(
        "Binary option",
        choices=["PR", "Branch", "RC", "Stable"]
    ).ask()
    evm_type = questionary.select(
        "What is the EVM type?",
        choices=["Anvil", "Sepolia"]
    ).ask()
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
        f"Maintenance environment: `{env_name}` {binary_option_text} [{env_type} Config]",
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
    create_subtask(
        api,
        "Perform maintenance work",
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

    env_name = questionary.text("Environment name?").ask()
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


def dev_releases_rc_from_hotfix_branch(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    version = questionary.text("New package version?").ask()
    branch_num = questionary.text("Hotfix branch number?").ask()
    stripped_version = ".".join(version.split(".")[:-1])
    branch_name = f"rc-{stripped_version}-hotfix{branch_num}"

    create_task(
        api,
        f"`{version}` hotfix: merge all relevant PRs",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

    task = create_task(
        api,
        f"`{version}` hotfix: create Discourse thread for RC",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    for subtask_title in [
        f"Obtain the PR numbers using `git log stable..{branch_name} --oneline`",
        "Generate the report",
    ]:
        create_subtask(
            api,
            subtask_title,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    task = create_task(
        api,
        f"`{version}` hotfix: produce release candidate",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    rc_tasks = [
        f"On `{branch_name}`: use `bump_version_for_rc.sh` script to get rc-based versions",
        f"On `{branch_name}`: increment `release-cycle-counter` in the `release-cycle-info` file",
        f"On `{branch_name}`: increment `RELEASE_CYCLE_COUNTER` in the `release_info.rs` file",
        f"On `{branch_name}`: create a `chore(release): release candidate {version}` commit",
        f"On `{branch_name}`: push the release commit",
        f"Run the `release` workflow with 4mb chunk size using {branch_name}",
        f"Update the Github release with the description"
    ]
    for rc_task in rc_tasks:
        create_subtask(
            api,
            rc_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    stable_release_tasks = [
        f"On `{branch_name}`: finalise the changelog",
        f"On `{branch_name}`: use `cargo release version release --execute` to bump from rc to stable versions",
        f"On `{branch_name}`: create a `chore(release): stable release {version}` commit",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `main`",
        "Push to `main`",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `stable`",
        "Push to `stable`",
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
    for stable_task in stable_release_tasks:
        create_subtask(
            api,
            stable_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    task = create_task(
        api,
        f"`{version}` hotfix: create Discourse thread for stable release",
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
    create_task(
        api,
        f"`{version}` hotfix: request community announcement",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)


def dev_releases_rc_hotfix(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    version = questionary.text("New package version?").ask()
    branch_num = questionary.text("Hotfix branch number?").ask()
    stripped_version = ".".join(version.split(".")[:-1])
    branch_name = f"rc-{stripped_version}-hotfix{branch_num}"

    task = create_task(
        api,
        f"`{version}` hotfix: create the RC branch",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

    create_task(
        api,
        f"`{version}` hotfix: merge all relevant PRs",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

    task = create_task(
        api,
        f"`{version}` hotfix: create Discourse thread for RC",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    for subtask_title in [
        f"Obtain the PR numbers using `git log stable..{branch_name} --oneline`",
        "Generate the report",
    ]:
        create_subtask(
            api,
            subtask_title,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    task = create_task(
        api,
        f"`{version}` hotfix: produce release candidate",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    rc_tasks = [
        f"On `{branch_name}`: use `bump_version_for_rc.sh` script to get rc-based versions",
        f"On `{branch_name}`: increment `release-cycle-counter` in the `release-cycle-info` file",
        f"On `{branch_name}`: increment `RELEASE_CYCLE_COUNTER` in the `release_info.rs` file",
        f"On `{branch_name}`: create a `chore(release): release candidate {version}` commit",
        f"On `{branch_name}`: push the release commit",
        f"Run the `release` workflow with 4mb chunk size using {branch_name}",
        f"Update the Github release with the description"
    ]
    for rc_task in rc_tasks:
        create_subtask(
            api,
            rc_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    stable_release_tasks = [
        f"On `{branch_name}`: finalise the changelog",
        f"On `{branch_name}`: use `cargo release version release --execute` to bump from rc to stable versions",
        f"On `{branch_name}`: create a `chore(release): stable release {version}` commit",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `main`",
        "Push to `main`",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `stable`",
        "Push to `stable`",
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
    for stable_task in stable_release_tasks:
        create_subtask(
            api,
            stable_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    task = create_task(
        api,
        f"`{version}` hotfix: create Discourse thread for stable release",
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
    create_task(
        api,
        f"`{version}` hotfix: request community announcement",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        apply_date=True,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

def dev_releases_rc_new(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    version = questionary.text("New package version?").ask()
    stripped_version = ".".join(version.split(".")[:-1])
    branch_name = f"rc-{stripped_version}"

    create_task(
        api,
        f"`{version}` RC: merge any outstanding PRs",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

    task = create_task(
        api,
        f"`{version}` RC: produce release candidate",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    rc_tasks = [
        f"Create and switch to new `{branch_name}` branch",
        "Use `git log stable..main --oneline --merges` to determine the PR numbers",
        "Put the PR numbers in a file",
        f"Use Claude to try and determine the crates to be bumped (check for breaking changes)",
        f"Use Claude's recommendations to bump crates with `cargo release`",
        f"Check `ant-protocol` does not have a `MAJOR` bump",
        f"Bump the `autonomi-nodejs` Node JS package if the Rust crate was bumped",
        f"Bump the `ant-node-nodejs` Node JS package if the Rust crate was bumped",
        f"Increment `release-cycle-counter` in the `release-cycle-info` file",
        f"Increment `RELEASE_CYCLE_COUNTER` in the `release_info.rs` file",
        f"Use Claude to generate an initial changelog",
        f"Review and improve the initial changelog",
        f"Create a `chore(release): release candidate {version}` commit",
        f"Push the release commit",
        f"Run the `release` workflow with 4mb chunk size using {branch_name}",
        f"Update the Github release with the description",
        f"Create a Discourse thread for reviewing the changelog",
        f"Create a new release candidate project in Linear"
    ]
    for rc_task in rc_tasks:
        create_subtask(
            api,
            rc_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)

    stable_release_tasks = [
        f"On `{branch_name}`: finalise the changelog",
        f"On `{branch_name}`: use `cargo release version release --execute` to bump from rc to stable versions",
        f"On `{branch_name}`: bump `autonomi-nodejs` from RC to stable version (if applicable)",
        f"On `{branch_name}`: bump `ant-node-nodejs` from RC to stable version (if applicable)",
        f"On `{branch_name}`: create a `chore(release): stable release {version}` commit",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `main`",
        "Push to `main`",
        f"Use `git merge --no-ff {branch_name}` to merge the RC branch to `stable`",
        "Push to `stable`",
        "Push tag to origin",
        "Prepare the release description",
        "Publish crates using `release-plz` from development machine",
        "Run the `release` workflow on the `stable` branch with a 4MB chunk size",
        "Update the Github release description",
        "On `stable`: publish crates with `release-plz`",
    ]
    task = create_task(
        api,
        f"`{version}`: stable release",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)
    for stable_task in stable_release_tasks:
        create_subtask(
            api,
            stable_task,
            CI_RELEASE_PROJECT_ID,
            task_type,
            work_type,
            task.id)


def dev_releases_rc_sneak(api):
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    version = questionary.text("New package version?").ask()
    task = create_task(
        api,
        f"Cut `{version}` sneak RC",
        CI_RELEASE_PROJECT_ID,
        task_type,
        work_type,
        section_id=CURRENT_RELEASE_CYCLE_SECTION_ID)

    for subtask_title in [
        "Merge all relevant PRs",
        "Pull any new changes into the RC branch",
        "Add the new PR numbers to my internal list",
        "Increment RC suffix for Rust crates: `cargo release version --workspace rc --execute`",
        "Increment RC suffix for NodeJS packages",
        "Consider if any versions need to be bumped manually",
        "Increment the counter in the `release-cycle-info` file",
        "Increment the counter in the `sn_build_info/src/release_info.rs` file",
        f"Create a new `chore(release): release candidate `{version}`",
        "Run the release workflow on the RC branch with 4mb chunk size",
        "Produce the release description",
        "Update the Github release description",
        "Update the changelog thread on Discourse",
        "Create a new project on Linear",
    ]:
        create_subtask(
            api,
            subtask_title,
            CI_RELEASE_PROJECT_ID,
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

def dev_environments_comparison_upload_report():
    start_time = questionary.text("Start time of the upload period:").ask()
    end_time = questionary.text("End time of the upload period:").ask()

    print("\nReference Environment:")
    ref_env_name = questionary.text("Environment name:").ask()
    ref_total_uploaders = questionary.text(
        "Total number of uploaders:",
        validate=lambda text: text.isdigit()
    ).ask()
    ref_successful_uploads = questionary.text(
        "Number of successful uploads:",
        validate=lambda text: text.isdigit()
    ).ask()
    ref_total_chunks = questionary.text(
        "Total chunks uploaded:",
        validate=lambda text: text.isdigit()
    ).ask()
    ref_avg_upload_time = questionary.text(
        "Average upload time (seconds):",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()
    ref_chunk_proof_error_count = questionary.text(
        "Number of chunk proof errors:",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()
    ref_not_enough_quotes_error_count = questionary.text(
        "Number of not enough quotes errors:",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()

    test_count = questionary.text(
        "\nNumber of test environments:",
        validate=lambda text: text.isdigit()
    ).ask()
    test_count = int(test_count)

    test_envs = []
    for i in range(test_count):
        print(f"\nTest Environment {i + 1}:")
        env_name = questionary.text("Environment name:").ask()
        env_data = {
            'name': env_name,
            'total_uploaders': questionary.text(
                "Total number of uploaders:",
                validate=lambda text: text.isdigit()
            ).ask(),
            'successful_uploads': questionary.text(
                "Number of successful uploads:",
                validate=lambda text: text.isdigit()
            ).ask(),
            'total_chunks': questionary.text(
                "Total chunks uploaded:",
                validate=lambda text: text.isdigit()
            ).ask(),
            'avg_upload_time': questionary.text(
                "Average upload time (seconds):",
                validate=lambda text: text.replace('.', '').isdigit()
            ).ask(),
            'chunk_proof_error_count': questionary.text(
                "Number of chunk proof errors:",
                validate=lambda text: text.replace('.', '').isdigit()
            ).ask(),
            'not_enough_quotes_error_count': questionary.text(
                "Number of not enough quotes errors:",
                validate=lambda text: text.replace('.', '').isdigit()
            ).ask()
        }
        test_envs.append(env_data)

    print()
    print("Uploads")
    print("=======")
    print(f"Period: {start_time} to {end_time}")
    for i, env in enumerate(test_envs):
        print(f"{env['name']}:")
        print(f"- Total uploaders: {env['total_uploaders']}")
        print(f"- Successful uploads: {env['successful_uploads']}")
        print(f"- Total chunks uploaded: {env['total_chunks']}")
        print(f"- Average upload time: {env['avg_upload_time']}s")

    print(f"{ref_env_name}:")
    print(f"- Total uploaders: {ref_total_uploaders}")
    print(f"- Successful uploads: {ref_successful_uploads}")
    print(f"- Total chunks uploaded: {ref_total_chunks}")
    print(f"- Average upload time: {ref_avg_upload_time}s")
    print(f"- Chunk proof errors: {ref_chunk_proof_error_count}")
    print(f"- Not enough quotes errors: {ref_not_enough_quotes_error_count}")


def dev_environments_test_upload_report():
    start_time = questionary.text("Start time of the upload period:").ask()
    end_time = questionary.text("End time of the upload period:").ask()

    env_name = questionary.text("Environment name:").ask()
    total_uploaders = questionary.text(
        "Total number of uploaders:",
        validate=lambda text: text.isdigit()
    ).ask()
    successful_uploads = questionary.text(
        "Number of successful uploads:",
        validate=lambda text: text.isdigit()
    ).ask()
    total_chunks = questionary.text(
        "Total chunks uploaded:",
        validate=lambda text: text.isdigit()
    ).ask()
    avg_upload_time = questionary.text(
        "Average upload time (seconds):",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()
    chunk_proof_error_count = questionary.text(
        "Number of chunk proof errors:",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()
    not_enough_quotes_error_count = questionary.text(
        "Number of not enough quotes errors:",
        validate=lambda text: text.replace('.', '').isdigit()
    ).ask()

    print()
    print("=======")
    print("Uploads")
    print("=======")
    print(f"Period: {start_time} to {end_time}")
    print(f"{env_name}:")
    print(f"- Total uploaders: {total_uploaders}")
    print(f"- Successful uploads: {successful_uploads}")
    print(f"- Total chunks uploaded: {total_chunks}")
    print(f"- Average upload time: {avg_upload_time}s")
    print(f"- Chunk proof errors: {chunk_proof_error_count}")
    print(f"- Not enough quotes errors: {not_enough_quotes_error_count}")

def is_issue_in_review(issue):
    """Check if a Linear issue has 'in review' status."""
    if not issue.state:
        return False
    state_name = issue.state.name.lower()
    return "in review" in state_name


def has_bug_label(issue):
    """Check if a Linear issue has the 'Bug' label."""
    if not hasattr(issue, 'labels') or not issue.labels:
        return False
    return any(label.name == "Bug" for label in issue.labels)


def _parse_linear_identifier(content):
    """Extract a Linear issue identifier from a Todoist task's content.

    Synced tasks are titled like "[V2-241](url): Title", but this also tolerates a
    bare "V2-241 ..." prefix. Returns a (team, number) tuple for sorting, or None if
    the content has no Linear issue prefix.
    """
    match = re.match(r"^\[?([A-Za-z][A-Za-z0-9]*)-(\d+)", content)
    if not match:
        return None
    return (match.group(1).upper(), int(match.group(2)))


def dev_order(api, args):
    """Reorder a project's top-level tasks by their Linear issue number.

    Linear-synced tasks carry an issue-number prefix (e.g. "V2-241"). Over time,
    syncing randomises the task order in the Todoist UI. This command sorts the
    prefixed tasks ascending by (team, issue number) and pushes any non-prefixed
    tasks to the bottom (preserving their current relative order).
    """
    project_name = args.project_name

    with console.status("[bold green]Fetching Todoist projects..."):
        todoist_projects = cache.cached_fetch(
            "todoist_projects",
            lambda: [p for page in api.get_projects() for p in page],
        )

    project_map = {p.name: p for p in todoist_projects}
    if project_name not in project_map:
        print(f"Error: Todoist project '{project_name}' not found.")
        return
    project = project_map[project_name]

    with console.status(f"[bold green]Fetching tasks for '{project_name}'..."):
        tasks = [t for page in api.get_tasks(project_id=project.id) for t in page]

    # Top-level tasks only; leave subtasks untouched.
    top_level_tasks = [t for t in tasks if getattr(t, "parent_id", None) is None]

    prefixed = []
    non_prefixed = []
    for task in top_level_tasks:
        identifier = _parse_linear_identifier(task.content)
        if identifier is None:
            non_prefixed.append(task)
        else:
            prefixed.append((identifier, task))

    if not prefixed:
        print(
            f"Error: no tasks in project '{project_name}' have a Linear issue "
            f"prefix (e.g. 'V2-241'). Nothing to order."
        )
        return

    # Sort prefixed tasks ascending by (team, number); keep non-prefixed in their
    # existing relative order at the bottom.
    prefixed.sort(key=lambda item: item[0])
    ordered_tasks = [task for _, task in prefixed] + non_prefixed

    _reorder_tasks(ordered_tasks)

    print(f"Reordered {len(ordered_tasks)} tasks in '{project_name}':")
    for position, task in enumerate(ordered_tasks, start=1):
        print(f"  {position:>3}. {task.content}")
    if non_prefixed:
        print(
            f"({len(non_prefixed)} task(s) without a Linear prefix were moved to "
            f"the bottom.)"
        )


def _reorder_tasks(ordered_tasks):
    """Set the in-project order of tasks via the Todoist Sync API.

    The todoist-api-python REST client has no reorder capability, so this issues an
    ``item_reorder`` command directly against the Sync API. Tasks are assigned a
    sequential 1-based child_order matching their position in ``ordered_tasks``.
    """
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise RuntimeError("TODOIST_API_TOKEN environment variable is not set")

    command = {
        "type": "item_reorder",
        "uuid": str(uuid.uuid4()),
        "args": {
            "items": [
                {"id": task.id, "child_order": position}
                for position, task in enumerate(ordered_tasks, start=1)
            ]
        },
    }

    with console.status("[bold green]Applying new task order..."):
        response = requests.post(
            "https://api.todoist.com/api/v1/sync",
            headers={"Authorization": f"Bearer {token}"},
            data={"commands": json.dumps([command])},
        )
        response.raise_for_status()
        result = response.json()

    sync_status = result.get("sync_status", {})
    status = sync_status.get(command["uuid"])
    if status != "ok" and isinstance(status, dict):
        raise RuntimeError(f"Todoist reorder failed: {status}")


def dev_sync_todoist_from_linear(api, args=None):
    """Sync issues from a Linear project to a Todoist project."""
    # Linear team configuration
    LINEAR_TEAMS = {
        "Infrastructure": "TODOIST_LINEAR_INFRA_API_KEY",
        "QA": "TODOIST_LINEAR_QA_API_KEY",
        "Releases": "TODOIST_LINEAR_RELEASES_API_KEY",
        "Tech": "TODOIST_LINEAR_TECH_API_KEY",
        "V2.0": "ANT_RUNNER_LINEAR_V2_API_KEY",
    }

    non_interactive = (
        args and args.linear_team and args.linear_project and args.todoist_project
    )
    no_cache = getattr(args, "no_cache", False)

    # Step 1: Select Linear team
    if non_interactive:
        selected_team = args.linear_team
        if selected_team not in LINEAR_TEAMS:
            print(f"Error: Unknown Linear team '{selected_team}'. Valid teams: {', '.join(LINEAR_TEAMS.keys())}")
            return
    else:
        team_choices = list(LINEAR_TEAMS.keys())
        selected_team = questionary.select(
            "Which Linear team do you want to sync from?",
            choices=team_choices
        ).ask()

        if not selected_team:
            print("No team selected. Exiting.")
            return

    # Get the API key for the selected team
    api_key_env_var = LINEAR_TEAMS[selected_team]
    linear_api_key = os.getenv(api_key_env_var)
    if not linear_api_key:
        print(f"Error: {api_key_env_var} environment variable is not set.")
        return

    # Step 2: Connect to Linear and get projects
    with console.status("[bold green]Connecting to Linear..."):
        linear_client = LinearClient(api_key=linear_api_key)
        teams = cache.cached_fetch(
            f"linear_teams_{selected_team}",
            lambda: linear_client.teams.get_all(),
            no_cache=no_cache,
        )

    if not teams:
        print("No teams found in Linear.")
        return

    # Get the first team (since we're using team-specific API keys)
    team = list(teams.values())[0]

    with console.status("[bold green]Fetching Linear projects..."):
        projects = cache.cached_fetch(
            f"linear_projects_{selected_team}",
            lambda: linear_client.projects.get_all(team_id=team.id),
            no_cache=no_cache,
        )

    if not projects:
        print("No projects found in Linear.")
        return

    # Step 3: Select a Linear project
    project_map = {p.name: p for p in projects.values()}

    if non_interactive:
        selected_project_name = args.linear_project
        if selected_project_name not in project_map:
            print(f"Error: Linear project '{selected_project_name}' not found. Available projects: {', '.join(project_map.keys())}")
            return
    else:
        project_choices = [f"{p.name}" for p in projects.values()]

        selected_project_name = questionary.select(
            "Which Linear project do you want to sync from?",
            choices=project_choices
        ).ask()

        if not selected_project_name:
            print("No project selected. Exiting.")
            return

    selected_linear_project = project_map[selected_project_name]

    # Step 4: Select Todoist project
    with console.status("[bold green]Fetching Todoist projects..."):
        todoist_projects = cache.cached_fetch(
            "todoist_projects",
            lambda: [p for page in api.get_projects() for p in page],
            no_cache=no_cache,
        )

    if non_interactive:
        todoist_project_map = {p.name: p for p in todoist_projects}
        selected_todoist_name = args.todoist_project
        if selected_todoist_name not in todoist_project_map:
            print(f"Error: Todoist project '{selected_todoist_name}' not found.")
            return
        selected_todoist_project = todoist_project_map[selected_todoist_name]
    else:
        # Filter to projects under the "Active Work Projects" section
        # The section_id for "Active Work Projects" is stored as a constant
        active_work_projects = [
            p for p in todoist_projects
            if hasattr(p, 'parent_id') and p.parent_id == str(ACTIVE_WORK_PROJECTS_SECTION_ID)
        ]

        # If no projects found under the section, fall back to all projects
        if not active_work_projects:
            # Try filtering by name containing "Active Work" as parent
            active_work_parent = next(
                (p for p in todoist_projects if "Active Work Projects" in p.name),
                None
            )
            if active_work_parent:
                active_work_projects = [
                    p for p in todoist_projects
                    if hasattr(p, 'parent_id') and p.parent_id == active_work_parent.id
                ]

        # If still no projects found, use all projects
        if not active_work_projects:
            active_work_projects = todoist_projects

        todoist_project_choices = [p.name for p in active_work_projects]
        todoist_project_map = {p.name: p for p in active_work_projects}

        selected_todoist_name = questionary.select(
            "Which Todoist project do you want to sync to?",
            choices=todoist_project_choices
        ).ask()

        if not selected_todoist_name:
            print("No Todoist project selected. Exiting.")
            return

        selected_todoist_project = todoist_project_map[selected_todoist_name]

    # Step 5: Get Linear issues (separate active from completed/cancelled)
    with console.status("[bold green]Fetching Linear issues..."):
        all_issues = linear_client.issues.get_by_project(selected_linear_project.id)
        active_issues = []
        completed_issues = []
        for issue in all_issues.values():
            state_name = issue.state.name.lower() if issue.state else ""
            state_type = issue.state.type.lower() if issue.state else ""
            if state_type in ["completed", "canceled", "cancelled"] or \
               state_name in ["done", "completed", "cancelled", "canceled"]:
                completed_issues.append(issue)
            else:
                active_issues.append(issue)

    if not active_issues and not completed_issues:
        print("No issues found in the Linear project.")
        return

    print(f"Found {len(active_issues)} active issues and {len(completed_issues)} completed/cancelled issues in Linear.")

    # Step 6: Get existing Todoist tasks to detect duplicates
    with console.status("[bold green]Fetching existing Todoist tasks..."):
        existing_tasks = [t for page in api.get_tasks(project_id=selected_todoist_project.id) for t in page]

    # Build a map of existing tasks by issue identifier
    existing_tasks_map = {}
    for task in existing_tasks:
        # Task titles are formatted like "[ABC-123](url): Title"
        # Extract the issue number from the beginning
        content = task.content
        if content.startswith("["):
            # Extract issue number between [ and ]
            end_bracket = content.find("]")
            if end_bracket > 0:
                issue_num = content[1:end_bracket]
                existing_tasks_map[issue_num] = task

    # Step 7: Create Todoist tasks for new issues
    created_count = 0
    updated_count = 0
    skipped_count = 0

    # Get the full label names (includes emoji prefixes)
    dev_labels = get_full_label_names(api, ["development"])
    in_review_label = get_full_label_names(api, ["in-review"])[0]
    in_progress_label = get_full_label_names(api, ["in-progress"])[0]
    bug_label = get_full_label_names(api, ["bug"])[0]

    for issue in active_issues:
        issue_identifier = issue.identifier  # e.g., "ABC-123"

        if issue_identifier in existing_tasks_map:
            existing_task = existing_tasks_map[issue_identifier]
            current_labels = existing_task.labels or []
            in_review = is_issue_in_review(issue)
            has_in_review = in_review_label in current_labels

            if in_review and not has_in_review:
                # Add the in-review label and remove in-progress if present
                new_labels = [l for l in current_labels if l != in_progress_label]
                new_labels.append(in_review_label)
                api.update_task(existing_task.id, labels=new_labels)
                updated_count += 1
                print(f"  Updated: {issue_identifier}: {issue.title} (added in-review label)")
            elif not in_review and has_in_review:
                # Remove the label
                new_labels = [l for l in current_labels if l != in_review_label]
                api.update_task(existing_task.id, labels=new_labels)
                updated_count += 1
                print(f"  Updated: {issue_identifier}: {issue.title} (removed in-review label)")
            else:
                skipped_count += 1
            continue

        # Format: [ABC-123](url): Title
        issue_url = issue.url if hasattr(issue, 'url') else f"https://linear.app/issue/{issue_identifier}"
        task_title = f"[{issue_identifier}]({issue_url}): {issue.title}"

        # Apply in-review and bug labels to new tasks if applicable
        labels = dev_labels.copy()
        if is_issue_in_review(issue):
            labels.append(in_review_label)
        if has_bug_label(issue):
            labels.append(bug_label)

        api.add_task(
            content=task_title,
            project_id=selected_todoist_project.id,
            labels=labels
        )
        print(f"  Created: {issue_identifier}: {issue.title}")
        created_count += 1

    # Step 8: Close Todoist tasks for completed/cancelled Linear issues
    completed_count = 0
    for issue in completed_issues:
        issue_identifier = issue.identifier
        if issue_identifier in existing_tasks_map:
            existing_task = existing_tasks_map[issue_identifier]
            api.complete_task(existing_task.id)
            print(f"  Completed: {issue_identifier}: {issue.title}")
            completed_count += 1

    print(f"\nSync complete!")
    print(f"  Created: {created_count} tasks")
    if updated_count > 0:
        print(f"  Updated: {updated_count} tasks")
    if completed_count > 0:
        print(f"  Completed: {completed_count} tasks")
    if skipped_count > 0:
        print(f"  Skipped (no changes): {skipped_count} tasks")


def dev_sync_linear_from_todoist(api, args=None):
    """Sync Todoist tasks to Linear issues: set In Progress for today's tasks."""
    LINEAR_TEAMS = {
        "Infrastructure": "TODOIST_LINEAR_INFRA_API_KEY",
        "QA": "TODOIST_LINEAR_QA_API_KEY",
        "Releases": "TODOIST_LINEAR_RELEASES_API_KEY",
        "Tech": "TODOIST_LINEAR_TECH_API_KEY",
        "V2.0": "ANT_RUNNER_LINEAR_V2_API_KEY",
    }

    non_interactive = (
        args and args.linear_team and args.linear_project and args.todoist_project
    )
    no_cache = getattr(args, "no_cache", False)

    # Step 1: Select Linear team
    if non_interactive:
        selected_team = args.linear_team
        if selected_team not in LINEAR_TEAMS:
            print(f"Error: Unknown Linear team '{selected_team}'. Valid teams: {', '.join(LINEAR_TEAMS.keys())}")
            return
    else:
        team_choices = list(LINEAR_TEAMS.keys())
        selected_team = questionary.select(
            "Which Linear team do you want to sync to?",
            choices=team_choices
        ).ask()

        if not selected_team:
            print("No team selected. Exiting.")
            return

    api_key_env_var = LINEAR_TEAMS[selected_team]
    linear_api_key = os.getenv(api_key_env_var)
    if not linear_api_key:
        print(f"Error: {api_key_env_var} environment variable is not set.")
        return

    # Step 2: Connect to Linear and get projects
    with console.status("[bold green]Connecting to Linear..."):
        linear_client = LinearClient(api_key=linear_api_key)
        teams = cache.cached_fetch(
            f"linear_teams_{selected_team}",
            lambda: linear_client.teams.get_all(),
            no_cache=no_cache,
        )

    if not teams:
        print("No teams found in Linear.")
        return

    team = list(teams.values())[0]

    with console.status("[bold green]Fetching Linear projects..."):
        projects = cache.cached_fetch(
            f"linear_projects_{selected_team}",
            lambda: linear_client.projects.get_all(team_id=team.id),
            no_cache=no_cache,
        )

    if not projects:
        print("No projects found in Linear.")
        return

    # Step 3: Select a Linear project
    project_map = {p.name: p for p in projects.values()}

    if non_interactive:
        selected_project_name = args.linear_project
        if selected_project_name not in project_map:
            print(f"Error: Linear project '{selected_project_name}' not found. Available projects: {', '.join(project_map.keys())}")
            return
    else:
        project_choices = [f"{p.name}" for p in projects.values()]

        selected_project_name = questionary.select(
            "Which Linear project do you want to sync to?",
            choices=project_choices
        ).ask()

        if not selected_project_name:
            print("No project selected. Exiting.")
            return

    selected_linear_project = project_map[selected_project_name]

    # Step 4: Select Todoist project
    with console.status("[bold green]Fetching Todoist projects..."):
        todoist_projects = cache.cached_fetch(
            "todoist_projects",
            lambda: [p for page in api.get_projects() for p in page],
            no_cache=no_cache,
        )

    if non_interactive:
        todoist_project_map = {p.name: p for p in todoist_projects}
        selected_todoist_name = args.todoist_project
        if selected_todoist_name not in todoist_project_map:
            print(f"Error: Todoist project '{selected_todoist_name}' not found.")
            return
        selected_todoist_project = todoist_project_map[selected_todoist_name]
    else:
        active_work_projects = [
            p for p in todoist_projects
            if hasattr(p, 'parent_id') and p.parent_id == str(ACTIVE_WORK_PROJECTS_SECTION_ID)
        ]

        if not active_work_projects:
            active_work_parent = next(
                (p for p in todoist_projects if "Active Work Projects" in p.name),
                None
            )
            if active_work_parent:
                active_work_projects = [
                    p for p in todoist_projects
                    if hasattr(p, 'parent_id') and p.parent_id == active_work_parent.id
                ]

        if not active_work_projects:
            active_work_projects = todoist_projects

        todoist_project_choices = [p.name for p in active_work_projects]
        todoist_project_map = {p.name: p for p in active_work_projects}

        selected_todoist_name = questionary.select(
            "Which Todoist project do you want to sync from?",
            choices=todoist_project_choices
        ).ask()

        if not selected_todoist_name:
            print("No Todoist project selected. Exiting.")
            return

        selected_todoist_project = todoist_project_map[selected_todoist_name]

    # Step 5: Fetch Linear issues and build identifier -> issue map
    with console.status("[bold green]Fetching Linear issues..."):
        all_issues = linear_client.issues.get_by_project(selected_linear_project.id)
        linear_issues_map = {}
        for issue in all_issues.values():
            linear_issues_map[issue.identifier] = issue

    print(f"Found {len(linear_issues_map)} issues in Linear project '{selected_project_name}'.")

    # Step 6: Fetch Todoist tasks
    with console.status("[bold green]Fetching Todoist tasks..."):
        todoist_tasks = [t for page in api.get_tasks(project_id=selected_todoist_project.id) for t in page]

    print(f"Found {len(todoist_tasks)} tasks in Todoist project '{selected_todoist_name}'.")

    # Step 7: Process each Todoist task
    today = date.today()
    updated_count = 0
    skipped_already_in_progress = 0
    skipped_in_review = 0
    skipped_no_today = 0
    skipped_no_identifier = 0
    warning_orphans = 0
    warning_duplicates = 0
    seen_identifiers = set()

    for task in todoist_tasks:
        content = task.content
        if not content.startswith("["):
            skipped_no_identifier += 1
            continue

        end_bracket = content.find("]")
        if end_bracket <= 0:
            skipped_no_identifier += 1
            continue

        issue_identifier = content[1:end_bracket]

        if issue_identifier in seen_identifiers:
            warning_duplicates += 1
            print(f"  Warning: Duplicate Todoist task for {issue_identifier}")
        seen_identifiers.add(issue_identifier)

        # Check for "Today" due date
        if not task.due or task.due.date != today:
            skipped_no_today += 1
            continue

        # Look up the Linear issue
        if issue_identifier not in linear_issues_map:
            warning_orphans += 1
            print(f"  Warning: {issue_identifier} not found in Linear project '{selected_project_name}'")
            continue

        issue = linear_issues_map[issue_identifier]

        # Check if In Review — do not change
        if is_issue_in_review(issue):
            skipped_in_review += 1
            print(f"  Skipped: {issue_identifier}: {issue.title} (In Review)")
            continue

        # Check if already In Progress
        state_name = issue.state.name.lower() if issue.state else ""
        if "in progress" in state_name:
            skipped_already_in_progress += 1
            print(f"  Already in progress: {issue_identifier}: {issue.title}")
            continue

        # Update to In Progress
        try:
            update_data = LinearIssueUpdateInput(stateName="In Progress")
            linear_client.issues.update(issue.id, update_data)
            print(f"  Updated: {issue_identifier}: {issue.title} -> In Progress")
            updated_count += 1
        except ValueError as e:
            raise RuntimeError(
                f"Failed to set 'In Progress' state for {issue_identifier}: {e}. "
                f"The 'In Progress' state may not be available for team '{selected_team}'."
            ) from e

    print(f"\nSync complete!")
    print(f"  Updated to In Progress: {updated_count}")
    if skipped_already_in_progress > 0:
        print(f"  Skipped (already In Progress): {skipped_already_in_progress}")
    if skipped_in_review > 0:
        print(f"  Skipped (In Review): {skipped_in_review}")
    if skipped_no_today > 0:
        print(f"  Skipped (no Today due date): {skipped_no_today}")
    if skipped_no_identifier > 0:
        print(f"  Skipped (no Linear identifier): {skipped_no_identifier}")
    if warning_duplicates > 0:
        print(f"  Warnings (duplicates): {warning_duplicates}")
    if warning_orphans > 0:
        print(f"  Warnings (orphaned references): {warning_orphans}")


#
# Helpers
#
def get_crate_version(toml_path):
    with open(toml_path, 'r') as file:
        cargo_toml = toml.load(file)
    return cargo_toml['package']['version']
