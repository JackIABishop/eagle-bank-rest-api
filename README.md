# Eagle Bank

Initial repository scaffold for the Eagle Bank take-home API.

## Source Material

- [openapi.yaml](openapi.yaml)
- [Authentication notes in JACK_NOTES.md](JACK_NOTES.md#authenticating-a-user)
- [Implementation checklist](docs/implementation-checklist.md)

The original PDF brief provided as part of the assessment is intentionally not included in version control. This repository keeps the implementation-facing contract in `openapi.yaml`, while omitting the supplied interview materials out of respect for the confidentiality of the take-home exercise.

## Reviewer Guide

If reviewing the project quickly, the most useful order is:

1. `openapi.yaml` for the supplied API contract
2. `README.md` for setup and project context
3. `docs/implementation-checklist.md` for what is and is not currently implemented
4. `JACK_NOTES.md` for design reasoning and working notes
5. `/docs` in the running app for the live FastAPI-generated documentation

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

## Run The API

Start the local development server with:

```bash
uvicorn app.main:app --reload
```

Once it is running, the main URLs are:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Run Tests

Run the current test suite with:

```bash
pytest
```

## Notes

- AI assistance was used to accelerate scaffolding and boilerplate during this take-home. I reviewed the generated code, aligned it to the API contract, and treated it as a starting point rather than something to trust blindly.
- SQLite is file-based, so there is no separate database server to start.
- `openapi.yaml` is the API contract for the implementation.
- As the application structure is built out, this README should be updated with the exact run and test commands for the project.
