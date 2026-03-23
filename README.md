# fastapi-app

A small birthday API using FastAPI, Pydantic, SQLAlchemy, and PostgreSQL.

## Endpoints

PUT /hello/{username}
- body: `{ "dateOfBirth": "YYYY-MM-DD" }`
- validation: username letters only, date before today
- response: 204 No Content

GET /hello/{username}
- response: `200` with message
- `Hello, <username>! Happy birthday!` if today
- `Hello, <username>! Your birthday is in N day(s)` otherwise

## Dev

1. Install dependencies:
   `uv sync --locked --all-extras`
2. Install pre commit hooks
   `pre-commit install`

## Run locally

1. Install dependencies:
   `uv sync --locked --all-extras`
2. Start PostgreSQL:
   `docker compose up db -d`
3. Set up `DATABASE_URL` if you are not using the default local container value.
4. Run app:
   `uv run uvicorn app.main:app --reload`

## Tests

Run unit tests:
`uv run pytest tests/unit -v`

Run integration tests against the containers:
1. `docker compose up --build -d`
2. `uv run pytest tests/integration -v`

## Manual testing

`docker compose up --build -d`

Go to http://localhost:8000/docs
