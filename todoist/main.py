import argparse
import os
import sys

from .cmd import \
    sept11_nist_assoc_dir_with_tape, \
    dev_releases_aw_release_checklist

from todoist_api_python.api import TodoistAPI


def get_args():
    parser = argparse.ArgumentParser(description="Create tasks in Todoist")
    main_subparser = parser.add_subparsers(dest="command", required=True)

    dev_parser = main_subparser.add_parser("dev", help="Manage dev tasks")
    dev_subparsers = dev_parser.add_subparsers(
        dest="dev_command",
        help="Manage dev tasks",
        required=True)
    release_parser = dev_subparsers.add_parser(
        "releases", help="Manage tasks related to release checklists")
    releases_subparsers = release_parser.add_subparsers(
        dest="releases_command",
        help="Release-related tasks",
        required=True)
    releases_subparsers.add_parser(
        "aw-release-checklist",
        help="Create a task for an Archive Witness release checklist")

    sept11_parser = main_subparser.add_parser(
        "sept11",
        help="Manage tasks for the 9/11 Archiving project")
    sept11_subparsers = sept11_parser.add_subparsers(
        dest="sept11_command",
        help="Manage tasks for the 9/11 Archiving project",
        required=True)
    nist_parser = sept11_subparsers.add_parser(
        "nist",
        help="Manage tasks for NIST")
    nist_subparsers = nist_parser.add_subparsers(
        dest="nist_command",
        help="NIST-related tasks",
        required=True)
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
    locate_parser.add_argument("--subtasks-path")

    food_parser = main_subparser.add_parser("food", help="Manage tasks for food")
    food_subparsers = food_parser.add_subparsers(
        dest="food_command",
        help="Manage tasks for food",
        required=True)
    food_subparsers.add_parser("add-item")

    return parser.parse_args()


def main():
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)
    args = get_args()
    if args.command == "sept11":
        if args.sept11_command == "nist":
            if args.nist_command == "assoc-dir-with-tape":
                sept11_nist_assoc_dir_with_tape(api, args.dir_list_path)
            elif args.nist_command == "locate-tape":
                print("Processing locate-tape command")
    elif args.command == "dev":
        if args.dev_command == "releases":
            if args.releases_command == "aw-release-checklist":
                dev_releases_aw_release_checklist(api)
    elif args.command == "food":
        if args.food_command == "add-item":
            print("Processing add-item command")


if __name__ == "__main__":
    sys.exit(main())
