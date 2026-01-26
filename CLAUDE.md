# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python CLI tool for automating Todoist task creation for personal workflow management. The tool provides structured commands for creating task hierarchies with predefined subtasks for various domains: software development workflows, food planning, film scheduling, finance, and 9/11 archiving research.

## Setup and Development

### Environment Setup

This project uses virtualfish for Fish shell:

```bash
vf new todoist-personal
vf activate todoist-personal
pip install -r requirements.txt
pip install -e .
```

### Required Environment Variables

- `TODOIST_API_TOKEN`: API token from Todoist Settings -> Integrations -> API token

### Running the CLI

```bash
todoist --help
todoist dev environments test  # Example: create test environment task
todoist food plan              # Example: create food planning tasks
```

## Architecture

### Command Structure

The CLI follows a hierarchical command pattern using argparse:
- **Main entry point**: `todoist/main.py` - Defines all argument parsers and routes to command handlers
- **Command modules**: `todoist/cmd/*.py` - Each module implements handlers for a domain (dev, food, films, finance, sept11)
- **Core utilities**:
  - `todoist/tasks.py` - Task creation functions with label/project management
  - `todoist/helpers.py` - Shared utilities (e.g., date_picker)

### Task Creation Pattern

All command handlers follow this pattern:
1. Use `questionary` to gather interactive input from the user
2. Call `create_task()` from `tasks.py` to create parent task with:
   - Project ID (hardcoded constants in command modules)
   - Task type enum (ADMIN, DEV, INVESTIGATION, RESEARCH)
   - Work type enum (WORK, PERSONAL)
   - Optional: apply_date, description, section_id
3. Call `create_subtask()` for each subtask in the workflow
4. Return task object

### Project IDs

Each domain has hardcoded Todoist project IDs defined as constants in the respective command module:
- `todoist/cmd/dev.py`: CI_RELEASE_PROJECT_ID, ENVIRONMENTS_PROJECT_ID, etc.
- `todoist/cmd/food.py`: SHOPPING_LIST_PROJECT_ID, LUNCH_PROJECT_ID, etc.

These IDs are specific to the user's Todoist account.

### Label System

Labels are automatically applied based on `TaskType` and `WorkType`:
- Work tasks get "work" label, personal tasks get "home" label
- Task types map to labels: DEV → "development", ADMIN → "admin" + "development", etc.
- Labels are matched by partial string search in `get_full_label_names()` - the full label name from Todoist is retrieved

### Food Management System

The food module (`todoist/cmd/food.py`) includes a SQLite-based system for:
- Managing food items with nutritional information
- Creating meals from food items
- Planning meals with automatic task creation in Todoist
- Database location: Determined at runtime (uses user's home directory)

## Development Patterns

### Adding New Commands

1. Add command definition in `main.py` `get_args()` function with appropriate subparsers
2. Create handler function in appropriate `todoist/cmd/*.py` module
3. Import and call handler in main.py's command routing logic (the large if/elif chain)
4. Follow existing patterns for questionary prompts and task creation

### Working with Versions

For release-related commands in `dev.py`:
- Version strings are typically in format "X.Y.Z"
- Use `stripped_version` pattern: `".".join(version.split(".")[:-1])` to get "X.Y" for branch names
- RC versions follow pattern: `rc-X.Y` or `rc-X.Y-hotfixN`

### File Generation

Some commands generate input files for external systems:
- `dev_deployments_upgrade()` generates YAML files in `DEPLOYMENT_INPUTS_PATH`
- Files are numbered sequentially and contain deployment specifications
- Use `shutil.rmtree()` to clean existing directories before regenerating

## Key Dependencies

- `todoist-api-python`: Official Todoist API client
- `questionary`: Interactive command-line prompts
- `rich`: Terminal formatting and status displays
- `toml`: Parse Cargo.toml files for version information (Archive Witness module)
