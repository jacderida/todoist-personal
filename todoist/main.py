import argparse
import os
import sys

from .cmd.dev import *
from .cmd.food import *
from .cmd.films import *
from .cmd.sept11 import *

from todoist_api_python.api import TodoistAPI


def get_args():
    parser = argparse.ArgumentParser(description="Create tasks in Todoist")
    main_subparser = parser.add_subparsers(dest="command", required=True)

    dev_parser = main_subparser.add_parser("dev", help="Create tasks for development")
    dev_subparsers = dev_parser.add_subparsers(
        dest="dev_command",
        help="Create tasks for development",
        required=True)

    deployments_parser = dev_subparsers.add_parser(
        "deployments", help="Create tasks for deployment checklists")
    deployments_subparsers = deployments_parser.add_subparsers(
        dest="deployments_command",
        help="Create tasks for deployment checklists",
        required=True)
    deployments_subparsers.add_parser(
        "upgrade",
        help="Create a task for an upgrade deployment")
    deployments_subparsers.add_parser(
        "generate-markdown-post",
        help="Generate the Discourse post for the deployment")

    environments_parser = dev_subparsers.add_parser(
        "environments", help="Create tasks related to environments")
    environments_subparsers = environments_parser.add_subparsers(
        dest="environments_command",
        help="Create tasks related to environments",
        required=True)
    environments_subparsers.add_parser(
        "comparison",
        help="Create a task for comparing two environments")
    environments_subparsers.add_parser(
        "test",
        help="Create a task for deploying an environment for a test")
    environments_subparsers.add_parser(
        "test-upload-report",
        help="Generate a report for upload metrics for a test environment")
    environments_subparsers.add_parser(
        "upscale-test",
        help="Create a task for deploying an environment for an upscale test")

    deployments_parser = dev_subparsers.add_parser(
        "releases", help="Create tasks for release checklists")
    releases_subparsers = deployments_parser.add_subparsers(
        dest="releases_command",
        help="Create tasks for release checklists",
        required=True)
    releases_subparsers.add_parser(
        "aw-release-checklist",
        help="Create a task for an Archive Witness release checklist")
    releases_subparsers.add_parser(
        "hotfix-existing-branches",
        help="Create tasks for performing a hotfix for branches that already exist as PRs")
    releases_subparsers.add_parser(
        "rc-hotfix",
        help="Create tasks for a hotfix release candidate")
    releases_subparsers.add_parser(
        "rc-from-hotfix-branch",
        help="Create tasks for a release candidate with an existing hotfix branch")
    releases_subparsers.add_parser(
        "rc-new",
        help="Create tasks for a release candidate from the main branch")
    releases_subparsers.add_parser(
        "rc-sneak",
        help="Create tasks for a new sneak release candidate")

    tests_parser = dev_subparsers.add_parser("tests", help="Create tasks for testing")
    tests_subparsers = tests_parser.add_subparsers(
        dest="tests_command", help="Create tasks for testing", required=True)
    tests_subparsers.add_parser(
        "nodeman-linux-smoke-test",
        help="Create a task with a checklist for a Linux smoke test for the node manager")
    tests_subparsers.add_parser(
        "nodeman-win-smoke-test",
        help="Create a task with a checklist for a Windows smoke test for the node manager")

    films_parser = main_subparser.add_parser("films", help="Create tasks for films")
    films_subparsers = films_parser.add_subparsers(
        dest="films_command", help="Create tasks for films", required=True)
    films_subparsers.add_parser("schedule", help="Create a task to schedule watching a film")

    food_parser = main_subparser.add_parser("food", help="Create tasks for food management")
    food_subparsers = food_parser.add_subparsers(
        dest="food_command", help="Create tasks for food management", required=True)

    food_subparsers.add_parser(
        "get-calories", help="Get the total calories for a given day on the plan")

    items_parser = food_subparsers.add_parser("items", help="Manage food items")
    items_subparsers = items_parser.add_subparsers(
        dest="items_command", help="Manage food items", required=True)
    items_subparsers.add_parser("add", help="Add an item to the shopping list")
    items_ls_parser = items_subparsers.add_parser("ls", help="List all the available food items")
    items_ls_parser.add_argument(
        "--details",
        action="store_true",
        help="Print the details of each item"
    )
    items_subparsers.add_parser("new", help="Create a new food item")
    items_rm_parser = items_subparsers.add_parser("rm", help="Remove a food item")
    items_rm_parser.add_argument(
        "id",
        type=int,
        help="The ID of the item to remove"
    )

    meals_parser = food_subparsers.add_parser("meals", help="Manage meals")
    meals_subparsers = meals_parser.add_subparsers(
        dest="meals_command", help="Manage meals", required=True)
    meals_subparsers.add_parser("ls", help="List all the available meals")
    meals_subparsers.add_parser("new", help="Create a new meal")
    meals_rm_parser = meals_subparsers.add_parser("rm", help="Remove a meal")
    meals_rm_parser.add_argument(
        "id",
        type=int,
        help="The ID of the item to remove"
    )

    plan_parser = food_subparsers.add_parser("plan", help="Create tasks for food planning")
    plan_parser.add_argument(
        "--repeat",
        action="store_true",
        help="Set this flag to work in repeat mode. Useful for adding the same item over a date range.")

    sept11_parser = main_subparser.add_parser(
        "sept11",
        help="Create tasks for 9/11 archiving/research")
    sept11_subparsers = sept11_parser.add_subparsers(
        dest="sept11_command",
        help="Create tasks for 9/11 archiving/research",
        required=True)
    nist_parser = sept11_subparsers.add_parser(
        "nist",
        help="Create tasks for NIST FOIA archiving/research/development")
    nist_subparsers = nist_parser.add_subparsers(
        dest="nist_command",
        help="Create tasks for NIST FOIA archiving/research/development",
        required=True)
    nist_subparsers.add_parser(
        "add-uncategorized",
        help="Create a task for adding an uncategorized directory or file")
    assoc_parser = nist_subparsers.add_parser(
        "assoc-dir-with-tape",
        help="Create a task for associating a directory with a tape from NIST's database")
    assoc_parser.add_argument(
        "--dir-list-path",
        help="""
A path to a file containing a list of directories to associate with tapes.

Each directory in the list will be created as a task.""")
    locate_parser = nist_subparsers.add_parser(
        "locate-tape",
        help="Create a task for locating a tape from NIST's database in the release files")
    locate_parser.add_argument("--tape-list-path")

    return parser.parse_args()


def main():
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)
    args = get_args()

    if args.command == "dev":
        if args.dev_command == "deployments":
            if args.deployments_command == "generate-markdown-post":
                dev_deployments_generate_markdown_post()
            elif args.deployments_command == "upgrade":
                dev_deployments_upgrade(api)
        elif args.dev_command == "environments":
            if args.environments_command == "comparison":
                dev_environments_comparison(api)
            elif args.environments_command == "test":
                dev_environments_test(api)
            elif args.environments_command == "test-upload-report":
                dev_environments_test_upload_report()
            if args.environments_command == "upscale-test":
                dev_environments_upscale_test(api)
        elif args.dev_command == "releases":
            if args.releases_command == "aw-release-checklist":
                dev_releases_aw_release_checklist(api)
            elif args.releases_command == "hotfix-existing-branches":
                dev_releases_hotfix_existing_branches(api)
            elif args.releases_command == "rc-from-hotfix-branch":
                dev_releases_rc_from_hotfix_branch(api)
            elif args.releases_command == "rc-hotfix":
                dev_releases_rc_hotfix(api)
            elif args.releases_command == "rc-new":
                dev_releases_rc_new(api)
            elif args.releases_command == "rc-sneak":
                dev_releases_rc_sneak(api)
        elif args.dev_command == "tests":
            if args.tests_command == "nodeman-linux-smoke-test":
                dev_tests_nodeman_linux_smoke_test(api)
            elif args.tests_command == "nodeman-win-smoke-test":
                dev_tests_nodeman_windows_smoke_test(api)
    elif args.command == "films":
        if args.films_command == "schedule":
            films_schedule(api)
    elif args.command == "food":
        if args.food_command == "get-calories":
            get_calories(api)
        if args.food_command == "items":
            if args.items_command == "add":
                items_add(api)
            elif args.items_command == "ls":
                items_ls(args.details)
            elif args.items_command == "new":
                items_new()
            elif args.items_command == "rm":
                items_rm(args.id)
        elif args.food_command == "meals":
            if args.meals_command == "ls":
                meals_ls()
            elif args.meals_command == "new":
                meals_new()
            elif args.meals_command == "rm":
                meals_rm(args.id)
        elif args.food_command == "plan":
            plan(api, args.repeat)
    elif args.command == "sept11":
        if args.sept11_command == "nist":
            if args.nist_command == "add-uncategorized":
                sept11_nist_add_uncategorized(api)
            elif args.nist_command == "assoc-dir-with-tape":
                sept11_nist_assoc_dir_with_tape(api, args.dir_list_path)
            elif args.nist_command == "locate-tape":
                sept11_nist_locate_tape(api, args.tape_list_path)


if __name__ == "__main__":
    sys.exit(main())
