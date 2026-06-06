# Eagle Bank

Initial repository scaffold for the Eagle Bank take-home API.

## Source Material

- [openapi.yaml](openapi.yaml)
- [Authentication notes in JACK_NOTES.md](JACK_NOTES.md#authenticating-a-user)

The original PDF brief provided as part of the assessment is intentionally not included in version control. This repository keeps the implementation-facing contract in `openapi.yaml`, while omitting the supplied interview materials out of respect for the confidentiality of the take-home exercise.

## Local Setup

### Prerequisites

- Python 3
- Git

### Create the virtual environment

```bash
python3 -m venv .venv
```

### Activate the virtual environment

```bash
source .venv/bin/activate
```

### Install the current project dependencies

```bash
pip install -r requirements.txt
```

## Notes

- SQLite is file-based, so there is no separate database server to start.
- `openapi.yaml` is the API contract for the implementation.
- As the application structure is built out, this README should be updated with the exact run and test commands for the project.
