# Todoist Personal

Scripts for automating the creation of tasks in my personal Todoist setup, which I use daily.

## Setup

To use with Fish, install [virtualfish](https://virtualfish.readthedocs.io/en/latest/install.html), then run the following commands:
```
vf new todoist-personal
vf activate todoist-personal
pip install -r requirements.txt
pip install -e .

todoist --help
```

The `TODOIST_API_TOKEN` must be set to the API token for the account. The token can be retrieved by going to `Todoist Settings -> Integrations -> API token`.
