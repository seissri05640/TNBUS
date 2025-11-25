# Services API

FastAPI application that powers the Traffic platform backend services.

## Local development

```sh
poetry install
poetry run uvicorn app.main:app --reload
```

The API exposes `/health` and `/version` endpoints that return diagnostic and release metadata. All
configuration is managed via typed [Pydantic settings](app/core/config.py) and can be overridden with
`API_`-prefixed environment variables (see `.env.example`).

## Testing & linting

```sh
poetry run pytest
poetry run ruff check app tests
```

## Database & migrations

1. Copy `.env.example` to `.env` and update `API_DATABASE_URL` for your Postgres instance.
2. Apply the schema: `poetry run alembic upgrade head`.
3. (Optional) Load sample entities: `poetry run python scripts/seed_data.py`.

The SQLAlchemy models live under `app/models/` and the Alembic configuration resides in
`alembic/`. Core entities created in the initial migration:

- `routes` — canonical definitions used for lookup by short code.
- `buses` — fleet vehicles with route assignments and status metadata.
- `telemetry_records` — GPS/ridership time series keyed by bus and timestamp.
- `traffic_snapshots` — periodic congestion/incident summaries from third parties.
- `predictions` — headway/ETA outputs that link routes to telemetry + traffic data.

## Docker

Build the container from the repository root (the Dockerfile lives alongside the service):

```sh
docker build -f services/api/Dockerfile -t traffic-api .
docker run --rm -p 8000:8000 traffic-api
```
