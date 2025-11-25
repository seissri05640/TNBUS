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

## Docker

Build the container from the repository root (the Dockerfile lives alongside the service):

```sh
docker build -f services/api/Dockerfile -t traffic-api .
docker run --rm -p 8000:8000 traffic-api
```
